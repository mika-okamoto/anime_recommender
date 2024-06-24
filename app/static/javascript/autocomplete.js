document.addEventListener('DOMContentLoaded', () => {
    const inputContainer = document.getElementById('autocomplete-container');
    const addInputButton = document.getElementById('add-input');
    const removeInputButton = document.getElementById('remove-input');
    const recommendButton = document.getElementById('recommend-button');

    // add a new input box with autocomplete
    const addInputBox = () => {
        const inputBox = document.createElement('div');
        const inputId = `autocomplete-input-${document.querySelectorAll('.autocomplete-input').length + 1}`;
        
        inputBox.innerHTML = `
            <input type="text" id="${inputId}" class="autocomplete-input" placeholder="Type an anime!" autocomplete = "off">
            <div class="suggestions" id="suggestions-${inputId}"></div>
        `;
        
        inputContainer.appendChild(inputBox);
        addAutocompleteFunctionality(inputId);
        saveInputState();
    };

    // remove the last input box
    const removeInputBox = () => {
        const inputBoxes = document.querySelectorAll('.autocomplete-input');
        if (inputBoxes.length > 1) {
            inputBoxes[inputBoxes.length - 1].parentNode.remove();
            saveInputState();
        }
    };

    // add autocomplete functionality to input box
    const addAutocompleteFunctionality = (inputId) => {
        const inputElement = document.getElementById(inputId);
        const suggestionsBox = document.getElementById(`suggestions-${inputId}`);

        inputElement.addEventListener('input', function() {
            let query = this.value;
            if (query.length > 0) {
                fetch(`/autocomplete?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        suggestionsBox.innerHTML = '';
                        data.forEach(item => {
                            let suggestionItem = document.createElement('div');
                            suggestionItem.classList.add('suggestion-item');
                            suggestionItem.textContent = item;
                            suggestionsBox.appendChild(suggestionItem);
                        });
                        suggestionsBox.style.display = 'block';
                    });
            } else {
                suggestionsBox.style.display = 'none';
            }
            saveInputState();
        });

        // hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!suggestionsBox.contains(e.target) && e.target.id !== inputId) {
                suggestionsBox.style.display = 'none';
            }
        });

        // populate input when suggestion is clicked
        suggestionsBox.addEventListener('click', function(e) {
            if (e.target.classList.contains('suggestion-item')) {
                inputElement.value = e.target.textContent;
                suggestionsBox.style.display = 'none';
            }
            saveInputState();
        });
    };

    const saveInputState = () => {
        const inputValues = Array.from(document.querySelectorAll('.autocomplete-input')).map(input => input.value);
        localStorage.setItem('inputValues', JSON.stringify(inputValues));
    };

    const loadInputState = () => {
        const inputValues = JSON.parse(localStorage.getItem('inputValues'));
        if (inputValues) {
            inputValues.forEach(value => {
                addInputBox();
                inputContainer.lastElementChild.querySelector('.autocomplete-input').value = value;
            });
        }
    };

    addInputButton.addEventListener('click', addInputBox);

    removeInputButton.addEventListener('click', removeInputBox);

    recommendButton.addEventListener('click', (event) => {
        const len = document.querySelectorAll('.autocomplete-input').length;
        saveInputState();

        const names = [];
        let inputValid = true;

        for (let i = 1; i <= len; i++) {
            if (document.getElementById(`autocomplete-input-${i}`).value == "") inputValid = false;
            names.push(document.getElementById(`autocomplete-input-${i}`).value);
        }

        $('#recommendations-container').empty();

        const container = document.getElementById('recommendations-container');

        if (!inputValid) {
            const header = document.createElement('h4');
            header.textContent = "Please fill in all inputs!";
            container.appendChild(header);
        } else {
            const header = document.createElement('h3');
            header.textContent = "Recommendations for " + names.join(', ')
            container.appendChild(header);

            const loadingElement = document.createElement('h3');
            loadingElement.setAttribute('id', 'loading-bar');
            container.appendChild(loadingElement);

            const loadingInterval = loadingBar(loadingElement);

            fetch(`/recommend?q=${names.join(',')}`)
                .then(response => response.json())
                .then(recommendations => {
                    clearInterval(loadingInterval);
                    container.removeChild(loadingElement);
                    
                    if (recommendations == "No Recommendations Found") {
                        const paraItem = document.createElement('p')
                        paraItem.textContent = "No Recommendations Found";
                        container.appendChild(paraItem);
                    } else {
                        const table = document.createElement('table');
                        table.setAttribute('id', 'recommendations-table');

                        container.appendChild(table);

                        $('#recommendations-table').html(recommendations);

                        $('#recommendations-table').DataTable({
                            "paging": true,
                            "searching": true,
                            "ordering": true
                        });
                        
                    }
                }).catch(error => console.error('Error:', error));
            }
    })
    
    loadInputState();

    if (document.querySelectorAll('.autocomplete-input').length == 0) {
        addInputBox();
    }
});

function loadingBar(element) {
    const frames = ['.', '. .  ', '. . . ', '. . . .', '. . . . .', '. . . . . .', '. . . . . . .', '. . . . . . . .', '. . . . . . . . .', '. . . . . . . . . .'];
    let frameIndex = 0;

    const interval = setInterval(() => {
        element.textContent = 'Loading: ' + frames[frameIndex];
        frameIndex = (frameIndex + 1) % frames.length;
    }, 400);

    return interval;
}