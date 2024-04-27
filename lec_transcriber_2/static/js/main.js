$(document).ready(function() {
    let recognition;
    const startRecordButton = document.getElementById('startRecord');
    const stopRecordButton = document.getElementById('stopRecord');
    const saveNoteButton = document.getElementById('saveNote');
    const recordingIcon = document.getElementById('recordingIcon');
    const transcriptionDiv = document.getElementById('transcription');
    const savedNotesContainer = document.querySelector('.saved-notes-container');

    startRecordButton.addEventListener('click', startRecording);
    stopRecordButton.addEventListener('click', stopRecording);

    let isAlternate = false; // Variable to track alternating colors

    function startRecording() {
        transcriptionDiv.innerHTML = ''; // Clear previous transcription
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = function() {
            console.log('Recording started');
            recordingIcon.classList.remove('hidden');
            startRecordButton.disabled = true;
            stopRecordButton.disabled = false;
            saveNoteButton.disabled = true;
        };

        recognition.onresult = function(event) {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    transcriptionDiv.innerHTML += event.results[i][0].transcript + ' ';
                } else {
                    interimTranscript += event.results[i][0].transcript + ' ';
                }
            }
            console.log(interimTranscript);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onend = function() {
            console.log('Recording stopped');
            recordingIcon.classList.add('hidden');
            startRecordButton.disabled = false;
            stopRecordButton.disabled = true;
            saveNoteButton.disabled = false;
        };

        recognition.start();
    }

    function stopRecording() {
        recognition.stop();
    }

    saveNoteButton.addEventListener('click', function() {
        let transcriptionText = transcriptionDiv.innerText.trim();
        if (transcriptionText !== '') {
            let noteTitle = "Untitled";
            let noteContent = transcriptionText;
            let noteDate = new Date().toLocaleString();
            addSavedNoteElement(noteTitle, noteContent, noteDate);
            isAlternate = !isAlternate; // Toggle the value for alternating colors
        }
    });

    function addSavedNoteElement(noteTitle, noteContent, noteDate) {
        let note = document.createElement('div');
        note.classList.add('saved-note');
        note.classList.add(isAlternate ? 'alternate-color' : 'default-color'); // Add class for alternating colors
        note.innerHTML = `
            <input type="text" class="note-title bg-transparent border-b-2 border-gray-400 focus:outline-none focus:border-blue-500" value="${noteTitle}">
            <div class="note-content">
                <textarea class="bg-transparent border border-gray-300 rounded-md p-2">${noteContent}</textarea>
            </div>
            <p class="note-date">Created: ${noteDate}</p>
            <button class="deleteNote mt-2 bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600">Delete</button>
            <button class="downloadNote mt-2 bg-blue-500 text-white px-3 py-1 rounded-md hover:bg-blue-600">Download</button>
            <button class="summarizeNote mt-2 bg-yellow-500 text-white px-3 py-1 rounded-md hover:bg-yellow-600">Summarize</button>
            <div class="summarized-note-container"></div>
            <button class="generateFlashcard mt-2 bg-purple-500 text-white px-3 py-1 rounded-md hover:bg-purple-600">Generate Flashcard</button>
        `;
        savedNotesContainer.appendChild(note);
    }

    $(document).on('click', '.deleteNote', function() {
        $(this).parent('.saved-note').remove();
    });

    $(document).on('click', '.downloadNote', function() {
        let noteContent = $(this).siblings('.note-content').find('textarea').val();
        let noteTitle = $(this).siblings('.note-title').val();
        let blob = new Blob([noteContent], { type: 'text/plain' });
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = noteTitle + '.txt';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    $(document).on('click', '.summarizeNote', function() {
        let noteContent = $(this).siblings('.note-content').find('textarea').val();
        if (noteContent.trim() !== '') {
            summarizeNoteContent(noteContent, $(this).parent('.saved-note'));
        } else {
            console.error('Cannot summarize an empty note.');
        }
    });
    
    function summarizeNoteContent(content, savedNote) {
        $.ajax({
            url: '/summarize_note', // Change this to the appropriate endpoint on your server
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ content: content }),
            success: function(response) {
                console.log('Summarized note:', response.summary);
                displaySummarizedContent(response.summary, savedNote);
            },
            error: function(xhr, status, error) {
                console.error('Error summarizing note:', error);
            }
        });
    }
    
    function displaySummarizedContent(summary, savedNote) {
        // Split the summary into sentences
        let sentences = summary.split('. ');
        
        // Limit the summary to 40-70 words
        let summaryWords = [];
        let wordCount = 0;
        for (let sentence of sentences) {
            let words = sentence.split(' ');
            if (wordCount + words.length <= 70) {
                summaryWords.push(sentence);
                wordCount += words.length;
            } else {
                break;
            }
        }
        let summarizedText = summaryWords.join('. ') + '.';
        
        // Create bullet points
        let bulletPoints = summarizedText.split('. ').map(point => `<li>${point}</li>`).join('');

        // Create a new element for the summarized content
        let summarizedElement = document.createElement('div');
        summarizedElement.classList.add('summarized-note');
        summarizedElement.innerHTML = `
            <div class="bg-lime-green-500 border border-green-400 rounded-md p-4 mt-2">
                <ul>${bulletPoints}</ul>
                <button class="downloadSummarizedNote mt-2 bg-blue-500 text-white px-3 py-1 rounded-md hover:bg-blue-600">Download Summary</button>
            </div>
        `;
        // Append the summarized content to the UI, on the right side of the saved note
        $(savedNote).find('.summarized-note-container').html(summarizedElement);
    }

    $(document).on('click', '.downloadSummarizedNote', function() {
        let summarizedContent = $(this).siblings('ul').text();
        let blob = new Blob([summarizedContent], { type: 'text/plain' });
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = 'summarized_note.txt';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // JavaScript to add effects to the title and tagline
document.addEventListener('DOMContentLoaded', function() {
    const titleElement = document.getElementById('title');
    const taglineElement = document.getElementById('tagline');

    // Add effects using setTimeout for delay
    setTimeout(() => {
        titleElement.style.color = '#007bff'; // Change color to blue
    }, 500);

    setTimeout(() => {
        taglineElement.style.color = '#007bff'; // Change color to blue
    }, 1000);
});



});
// Flashcard generating system
$(document).on('click', '.generateFlashcard', function() {
    let noteContent = $(this).siblings('.note-content').find('textarea').val();
    let noteTitle = $(this).siblings('.note-title').val();

    // Here you can send the note content and title to your server to generate flashcards
    // For demonstration purposes, let's just log the note content and title
    console.log('Generating flashcards for:', noteTitle);
    console.log('Note content:', noteContent);
});

// JavaScript to add effects to the title and tagline
document.addEventListener('DOMContentLoaded', function() {
    const titleElement = document.getElementById('title');
    const taglineElement = document.getElementById('tagline');

    // Add effects using setTimeout for delay
    setTimeout(() => {
        titleElement.style.color = '#007bff'; // Change color to blue
    }, 500);

    setTimeout(() => {
        taglineElement.style.color = '#007bff'; // Change color to blue
    }, 1000);
});

