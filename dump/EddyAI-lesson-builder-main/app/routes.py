import os
import datetime
from flask import request, jsonify, render_template
from flask_basicauth import BasicAuth
from app import app
from .model_script.model_rerun import generate_response

basic_auth = BasicAuth(app)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'}), 200

@app.route('/logs')
@basic_auth.required
def view_logs():
    log_file_path = 'logs/' + datetime.datetime.now().strftime("%Y-%m-%d") + '-app.log'
    
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.read()

        return render_template('logs.html', log_content=log_content)
    else:
        return 'Log file not found.'

@app.route('/generate-response', methods=['POST'])
def generate_lesson_package():
    try:
        req = request.get_json()
        required_input = ['topic', 'grade', 'subject', 'software', 'gen_tech_domain', 'recommendations', 'domain_list']

        if not all(k in req for k in required_input):
            return jsonify({'error': 'Missing required input'}), 400
        
        res, recommendations, gen_tech_domain, domain_list = generate_response(
            req['topic'],
            req['subject'],
            req['grade'],
            req['student_profile'],
            req['gen_tech_domain'],
            req['software'],
            req['tech_domain'],
            req['recommendations'],
            req['LP'],
            req['domain_list'],
            max_retry=5
        )

        res = {
            'core': {
                'summary': res['summary'],
                'topic': res['topic'],
                'grade': res['grade'],
                'subject': res['subject'],
                'tech domain': res['tech_domain'],
                'software': res['software'],
            },
            'key_concepts': res['key_concepts'],
            'prior_knowledge': res['prior_knowledge'],
            'objectives': res['objectives'],
            'outcomes': res['outcomes'],
            'real_world_application': res['real_world_application'],
            'lesson_overview': res['lesson_overview'],
            'pre_lesson_preparation': res['pre_lesson_preparation'],
            'troubleshooting': res['troubleshooting'],
            'assessment': res['assessment'],
            'detailed_slides': res['detailed_slides'],
            "gen_tech_domain": gen_tech_domain,
            "recommendations": recommendations,
            "domain_list": domain_list,
        }

        return jsonify(res), 200
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({'error': str(e)}), 500
