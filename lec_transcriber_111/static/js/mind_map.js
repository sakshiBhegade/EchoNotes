$(document).ready(function() {
    $('#generateMindMap').click(function() {
        var input = $('#mindMapInput').val();
        if (input.trim() === '') {
            alert('Please enter some text or a document to generate a mind map.');
            return;
        }

        $.ajax({
            url: '/generate_mind_map',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'content': input }),
            success: function(response) {
                if (response.error) {
                    alert(response.error);
                } else {
                    $('#mindMapResult').html('<pre>' + response.mind_map + '</pre>');
                }
            },
            error: function(xhr, status, error) {
                alert('An error occurred while generating the mind map.');
            }
        });
    });
});
