import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from nltk.corpus import stopwords
import nltk
import os

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class LegalML:
    def __init__(self, model_path='legal_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.vectorizer = None
        self.load_or_train()

    def get_legal_data(self):
        """Get training data for legal categories"""
        legal_data = {
            'Contract Law': [
                'agreement between parties',
                'contract terms and conditions',
                'breach of contract',
                'offer and acceptance',
                'consideration in contract',
                'contract disputes',
                'written agreements',
                'contract enforcement',
                'contractual obligations',
                'agreement dispute resolution'
            ],
            'Employment Law': [
                'employment contract',
                'workplace discrimination',
                'wrongful termination',
                'employee rights',
                'wage and hour laws',
                'harassment at work',
                'leave policies',
                'workplace safety',
                'employee benefits',
                'labor regulations'
            ],
            'Property Law': [
                'real estate transaction',
                'property rights',
                'land ownership',
                'property deed',
                'tenant and landlord',
                'property dispute',
                'boundary issues',
                'property inheritance',
                'real estate contract',
                'property title'
            ],
            'Family Law': [
                'divorce proceedings',
                'child custody',
                'child support',
                'alimony payment',
                'marriage dissolution',
                'family disputes',
                'adoption process',
                'spousal support',
                'custody arrangement',
                'family agreement'
            ],
            'Intellectual Property': [
                'patent protection',
                'copyright infringement',
                'trademark registration',
                'intellectual property rights',
                'patent application',
                'brand protection',
                'licensing agreement',
                'ip dispute',
                'trade secret protection',
                'intellectual property violation'
            ],
            'Criminal Law': [
                'criminal charges',
                'felony conviction',
                'misdemeanor offense',
                'criminal defense',
                'arrest warrant',
                'criminal prosecution',
                'plea bargain',
                'criminal liability',
                'crime victim',
                'criminal sentencing'
            ],
            'Liability Law': [
                'personal injury',
                'negligence claim',
                'liability insurance',
                'accident compensation',
                'injury lawsuit',
                'damages claim',
                'liability dispute',
                'fault determination',
                'injury case',
                'compensatory damages'
            ]
        }
        return legal_data

    def prepare_training_data(self):
        """Prepare training data"""
        legal_data = self.get_legal_data()
        X_train = []
        y_train = []
        
        for category, phrases in legal_data.items():
            for phrase in phrases:
                X_train.append(phrase)
                y_train.append(category)
        
        return X_train, y_train

    def train_model(self):
        """Train the ML model"""
        X_train, y_train = self.prepare_training_data()
        
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                stop_words=list(stopwords.words('english')),
                ngram_range=(1, 2),
                min_df=1
            )),
            ('clf', MultinomialNB())
        ])
        
        self.model.fit(X_train, y_train)
        self.save_model()

    def save_model(self):
        """Save model to disk"""
        joblib.dump(self.model, self.model_path)

    def load_or_train(self):
        """Load existing model or train new one"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self.train_model()
        else:
            self.train_model()

    def predict_category(self, text):
        """Predict category with confidence"""
        if not self.model:
            return None, 0.0
        
        try:
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            confidence = max(probabilities)
            
            return prediction, float(confidence)
        except:
            return None, 0.0

    def get_legal_info(self, category):
        """Get detailed legal information for category"""
        legal_info = {
            'Contract Law': {
                'description': 'Law governing agreements between parties',
                'key_elements': ['Offer', 'Acceptance', 'Consideration', 'Intent', 'Capacity'],
                'advice': 'Always review contracts carefully. Seek legal advice before signing important agreements.'
            },
            'Employment Law': {
                'description': 'Law governing employer-employee relationships',
                'key_elements': ['Employment Contract', 'Wages', 'Working Hours', 'Discrimination', 'Safety'],
                'advice': 'Know your rights at work. Report discrimination and unsafe conditions promptly.'
            },
            'Property Law': {
                'description': 'Law governing ownership and use of property',
                'key_elements': ['Title', 'Deed', 'Ownership', 'Landlord', 'Tenant'],
                'advice': 'Get property inspections. Ensure clear title before purchase. Know tenant rights.'
            },
            'Family Law': {
                'description': 'Law governing family relationships and domestic matters',
                'key_elements': ['Marriage', 'Divorce', 'Custody', 'Support', 'Adoption'],
                'advice': 'Document agreements. Prioritize children\'s welfare. Consider mediation.'
            },
            'Intellectual Property': {
                'description': 'Law protecting creative works and inventions',
                'key_elements': ['Patent', 'Copyright', 'Trademark', 'Trade Secret', 'License'],
                'advice': 'Register your intellectual property. Use proper notices. Document creation dates.'
            },
            'Criminal Law': {
                'description': 'Law regarding criminal offenses and prosecution',
                'key_elements': ['Crime', 'Prosecution', 'Defense', 'Evidence', 'Sentencing'],
                'advice': 'Exercise your right to remain silent. Request an attorney immediately if arrested.'
            },
            'Liability Law': {
                'description': 'Law governing compensation for harm or injury',
                'key_elements': ['Negligence', 'Injury', 'Damages', 'Insurance', 'Liability'],
                'advice': 'Document incidents. Seek medical attention. Report accidents promptly.'
            }
        }
        return legal_info.get(category, {})

    def generate_advice(self, category, case_description):
        """Generate legal advice based on category"""
        legal_advice = {
            'Contract Law': [
                'Ensure all terms are clearly written and understood by all parties.',
                'Have a lawyer review the contract before signing.',
                'Keep copies of all signed agreements.'
            ],
            'Employment Law': [
                'Keep records of all communications with your employer.',
                'Know your employment contract terms and conditions.',
                'Report violations to HR or relevant authorities.'
            ],
            'Property Law': [
                'Get a professional property inspection.',
                'Verify property title and ownership history.',
                'Understand local zoning and rental laws.'
            ],
            'Family Law': [
                'Document all agreements in writing.',
                'Consider mediation for disputes.',
                'Prioritize the welfare of any children involved.'
            ],
            'Intellectual Property': [
                'Register your intellectual property promptly.',
                'Use appropriate copyright and trademark notices.',
                'Monitor for unauthorized use of your work.'
            ],
            'Criminal Law': [
                'Exercise your right to remain silent.',
                'Request legal representation immediately.',
                'Do not sign anything without your attorney present.'
            ],
            'Liability Law': [
                'Document all accidents and injuries thoroughly.',
                'Gather evidence and witness information.',
                'Report incidents to relevant parties promptly.'
            ]
        }
        return legal_advice.get(category, ['Consult with a legal professional.'])
