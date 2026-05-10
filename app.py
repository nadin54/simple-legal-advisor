from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database import LegalDatabase
from ml_model import LegalML
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize database and ML model
db = LegalDatabase()
ml = LegalML()

# Legal categories info
LEGAL_CATEGORIES = {
    'Contract Law': {
        'description': 'Law governing agreements between parties',
        'keywords': ['contract', 'agreement', 'terms', 'breach', 'obligation']
    },
    'Employment Law': {
        'description': 'Law governing employer-employee relationships',
        'keywords': ['employment', 'workplace', 'discrimination', 'termination', 'wage']
    },
    'Property Law': {
        'description': 'Law governing ownership and use of property',
        'keywords': ['property', 'real estate', 'landlord', 'tenant', 'deed']
    },
    'Family Law': {
        'description': 'Law governing family relationships',
        'keywords': ['divorce', 'custody', 'child', 'marriage', 'support']
    },
    'Intellectual Property': {
        'description': 'Law protecting creative works and inventions',
        'keywords': ['patent', 'copyright', 'trademark', 'intellectual', 'brand']
    },
    'Criminal Law': {
        'description': 'Law regarding criminal offenses',
        'keywords': ['criminal', 'crime', 'prosecution', 'arrest', 'conviction']
    },
    'Liability Law': {
        'description': 'Law governing compensation for harm or injury',
        'keywords': ['injury', 'negligence', 'liability', 'damages', 'accident']
    }
}

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all legal categories"""
    categories = [
        {'name': name, 'description': info['description']} 
        for name, info in LEGAL_CATEGORIES.items()
    ]
    return jsonify(categories)

@app.route('/api/category-info/<category>', methods=['GET'])
def get_category_info(category):
    """Get detailed info about a category"""
    if category not in LEGAL_CATEGORIES:
        return jsonify({'error': 'Category not found'}), 404
    
    info = ml.get_legal_info(category)
    return jsonify(info)

@app.route('/api/cases', methods=['GET'])
def get_cases():
    """Get all cases"""
    cases = db.get_all_cases()
    return jsonify(cases)

@app.route('/api/cases', methods=['POST'])
def create_case():
    """Create new case"""
    data = request.json
    case_id = db.create_case(
        title=data.get('title'),
        description=data.get('description'),
        priority=data.get('priority', 'Medium')
    )
    return jsonify({'id': case_id, 'message': 'Case created successfully'}), 201

@app.route('/api/cases/<int:case_id>', methods=['GET'])
def get_case(case_id):
    """Get specific case"""
    case = db.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    return jsonify(case)

@app.route('/api/cases/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    """Update case"""
    data = request.json
    db.update_case(
        case_id,
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category'),
        status=data.get('status'),
        priority=data.get('priority'),
        notes=data.get('notes')
    )
    return jsonify({'message': 'Case updated successfully'})

@app.route('/api/cases/<int:case_id>', methods=['DELETE'])
def delete_case(case_id):
    """Close/Delete case"""
    db.close_case(case_id)
    return jsonify({'message': 'Case closed successfully'})

@app.route('/api/cases/<int:case_id>/advice', methods=['GET'])
def get_case_advice(case_id):
    """Get advice for a case"""
    advice = db.get_case_advice(case_id)
    return jsonify(advice)

@app.route('/api/predict-category', methods=['POST'])
def predict_category():
    """Predict legal category for query"""
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    category, confidence = ml.predict_category(query)
    db.log_query(query, category)
    
    return jsonify({
        'category': category,
        'confidence': confidence
    })

@app.route('/api/generate-advice', methods=['POST'])
def generate_advice():
    """Generate legal advice"""
    data = request.json
    category = data.get('category')
    case_id = data.get('case_id')
    description = data.get('description')
    
    if not category:
        return jsonify({'error': 'Category required'}), 400
    
    advice_list = ml.generate_advice(category, description)
    
    # Store advice in database if case_id provided
    if case_id and advice_list:
        for advice in advice_list:
            db.add_advice(case_id, advice, 'ML', 0.85)
    
    return jsonify({'advice': advice_list})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get usage statistics"""
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback"""
    data = request.json
    case_id = data.get('case_id')
    rating = data.get('rating')
    comments = data.get('comments', '')
    
    if case_id and rating:
        db.add_feedback(case_id, rating, comments)
        return jsonify({'message': 'Feedback recorded successfully'}), 201
    
    return jsonify({'error': 'Case ID and rating required'}), 400

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'OK', 'message': 'Smart Legal Advisor API running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
