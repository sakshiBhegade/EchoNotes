import os
import logging
from flask import Flask, redirect, render_template, request, jsonify, url_for, session
import openai
from gtts import gTTS
from flask_cors import CORS
from datetime import datetime
import time

BASE_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'folders')
os.makedirs(BASE_FOLDER_PATH, exist_ok=True)

os.makedirs('static/audio', exist_ok=True)
app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'  # Necessary for using sessions

# Configure logging for error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set your OpenAI API key here
openai_api_key = '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'
openai.api_key = openai_api_key

def summarize_text(text):
    # Call OpenAI API to summarize the text using the recommended replacement model
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=text,
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route('/')
def index():
    if 'user' in session:
        # User is logged in, render the index.html template
        folders = os.listdir(BASE_FOLDER_PATH)
        return render_template('index.html', folders=folders)
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        # Handle POST request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Dummy authentication logic
        if username == 'admin' and password == 'password':
            session['user'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    else:
        # Handle GET request
        return render_template('login.html')

def create_new_folder(folder_name):
    folder_path = os.path.join(BASE_FOLDER_PATH, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        raise Exception("Folder already exists")

@app.route('/create-folder', methods=['POST'])
def create_folder():
    folder_name = request.form.get('name')
    try:
        create_new_folder(folder_name)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/folder/<folder_name>')
def folder(folder_name):
    # Here you would retrieve the contents or data related to the folder
    return render_template('folders/folder.html', folder_name=folder_name)

@app.route('/save_note', methods=['POST'])
def save_note():
    try:
        note_content = request.form['note_content']
        note_date = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format the date as YYYYMMDD_HHMMSS

        # Summarize the note content
        summarized_content = summarize_text(note_content)

        # Convert summarized content to audio
        tts = gTTS(summarized_content)
        audio_filename = f"{note_date}.mp3"
        audio_file_path = os.path.join('static', 'audio', audio_filename)
        tts.save(audio_file_path)

        # Return the summarized content and audio file path
        return jsonify({
            'message': 'Note saved successfully!',
            'summarized_content': summarized_content,
            'audio_file': url_for('static', filename=f'audio/{audio_filename}')
        })

    except Exception as e:
        logging.error(f"Error saving note: {e}")
        return jsonify({'error': 'An error occurred while saving the note.'})

@app.route('/delete_note', methods=['POST'])
def delete_note():
    try:
        # Here you can delete the note from your database or perform any other necessary operations
        return jsonify({'message': 'Note deleted successfully!'})
    except Exception as e:
        logging.error(f"Error deleting note: {e}")
        return jsonify({'error': 'An error occurred while deleting the note.'})

@app.route('/summarize_note', methods=['POST'])
def summarize_note():
    try:
        content = request.json['content']
        summarized_content = summarize_text(content)
        return jsonify({'summary': summarized_content})
    except Exception as e:
        logging.error(f"Error summarizing note: {e}")
        return jsonify({'error': 'An error occurred while summarizing the note.'})

@app.route('/save_note_to_folder', methods=['POST'])
def save_note_to_folder():
    try:
        folder_name = request.form['folder_name']
        note_content = request.form['note_content']
        folder_path = os.path.join(BASE_FOLDER_PATH, folder_name)

        # Save the note content to a file in the folder
        note_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        note_file_path = os.path.join(folder_path, note_filename)
        with open(note_file_path, 'w') as f:
            f.write(note_content)

        return jsonify({'message': 'Note saved to folder successfully!'})

    except Exception as e:
        logging.error(f"Error saving note to folder: {e}")
        return jsonify({'error': 'An error occurred while saving the note to the folder.'})

@app.route('/folder/<folder_name>')
def folder_view(folder_name):
    folder_path = os.path.join(BASE_FOLDER_PATH, folder_name)
    notes = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    audio_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    return render_template('folder.html', folder_name=folder_name, notes=notes, audio_files=audio_files)

@app.route('/add_note_to_folder', methods=['POST'])
def add_note_to_folder():
    folder_name = request.form['folder_name']
    note_content = request.form['note_content']
    folder_path = os.path.join(BASE_FOLDER_PATH, folder_name)

    # Save the note content to a file in the folder
    note_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    note_file_path = os.path.join(folder_path, note_filename)
    with open(note_file_path, 'w') as f:
        f.write(note_content)

    return jsonify({'message': 'Note added to folder successfully!'})

@app.route('/create-quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        note_content = request.form['note_content']
        
        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                response = openai.Completion.create(
                    engine="gpt-3.5-turbo-instruct",
                    prompt=f"Generate a quiz with a minimum of 7 and a maximum of 10 questions based on the following notes:\n\n{note_content}\n\nProvide questions with multiple choices, clearly marking the correct answer.",
                    temperature=0.5,
                    max_tokens=1500
                )

                questions_raw = response.choices[0].text.strip().split("\n\n")
                questions = []
                correct_answers = []

                for question_raw in questions_raw:
                    parts = question_raw.split('\n')
                    if len(parts) < 2:
                        continue

                    question_text = parts[0]
                    choices = parts[1:]
                    
                    if not choices:
                        continue

                    correct_answer = choices[0]
                    correct_answers.append(correct_answer)
                    questions.append({
                        "message": question_text,
                        "choices": sorted(choices)
                    })

                if not questions:
                    return jsonify({'error': 'No valid questions generated.'})

                session['quiz'] = questions
                session['correct_answers'] = correct_answers

                return render_template('quiz.html', quiz=questions)
            except openai.error.RateLimitError as e:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except openai.error.OpenAIError as e:
                logging.error(f"OpenAI API error: {e}")
                return jsonify({'error': str(e)}), 500

    return render_template('create_quiz.html')

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    questions = session.get('quiz')
    correct_answers = session.get('correct_answers')

    if not questions or not correct_answers:
        return jsonify({'error': 'No quiz found in the session.'})

    user_answers = [request.form.get(f'question{i + 1}') for i in range(len(questions))]

    score = 0
    for i, user_answer in enumerate(user_answers):
        if user_answer == correct_answers[i]:
            score += 1

    session.pop('quiz', None)
    session.pop('correct_answers', None)

    return jsonify({'score': score, 'total': len(questions), 'correct_answers': correct_answers})

@app.route('/create-mind-map', methods=['GET'])
def create_mind_map():
    return render_template('create_mind_map.html')

@app.route('/generate_mind_map', methods=['POST'])
def generate_mind_map():
    try:
        content = request.json['content']
        logging.info(f"Received content: {content}")
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=f"Generate a mind map from the following text:\n\n{content}",
            temperature=0.7,
            max_tokens=1000
        )
        logging.info(f"OpenAI response: {response}")
        mind_map_text = response.choices[0].text.strip()
        return jsonify({'mind_map': mind_map_text})
    except Exception as e:
        logging.error(f"Error generating mind map: {e}")
        return jsonify({'error': 'An error occurred while generating the mind map.'})

if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    app.run(debug=True)
