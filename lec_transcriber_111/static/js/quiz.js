document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('quiz-form');
    const resultDiv = document.getElementById('result');
    const scoreSpan = document.getElementById('score');
    const totalSpan = document.getElementById('total');

    quizForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(quizForm);
        const response = await fetch('/submit-quiz', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        scoreSpan.textContent = data.score;
        totalSpan.textContent = data.total;
        resultDiv.style.display = 'block';

        // Highlight correct and incorrect answers
        const questions = document.querySelectorAll('.question');
        questions.forEach((question, index) => {
            const choices = question.querySelectorAll('input[type="radio"]');
            choices.forEach((choice) => {
                if (choice.value === data.correct_answers[index]) {
                    choice.parentNode.style.border = '2px solid green';
                } else if (choice.checked) {
                    choice.parentNode.style.border = '2px solid red';
                }
            });
        });
    });
});
