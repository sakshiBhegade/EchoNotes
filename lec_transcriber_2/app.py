import os
import logging
from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    transcription = request.form['transcription']
    return jsonify({'transcription': transcription})

@app.route('/save_note', methods=['POST'])
def save_note():
    try:
        note_content = request.form['note_content']
        note_date = request.form['note_date']
        
        # Summarize the note content
        summarized_content = summarize_text(note_content)
        
        # Here you can save the note and summarized content to your database or perform any other necessary operations
        # For demonstration purposes, we'll just return the summarized content
        return jsonify({'message': 'Note saved successfully!', 'summarized_content': summarized_content})
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

@app.route('/generate_flashcards', methods=['POST'])
def generate_flashcards():
    try:
        # Receive the note content and title from the request
        data = request.json
        note_content = data['note_content']
        note_title = data['note_title']

        # Here you can generate flashcards based on the note content and title
        # For demonstration purposes, let's just return the note content and title as flashcards
        flashcards = [{'title': note_title, 'content': note_content}]

        # Return the flashcards as JSON
        return jsonify({'flashcards': flashcards})
    except Exception as e:
        logging.error(f"Error generating flashcards: {e}")
        return jsonify({'error': 'An error occurred while generating flashcards.'})

if __name__ == '__main__':
    app.run(debug=True)
