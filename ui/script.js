// parses the conversation in the log file
function parser(str) {
    //splits the conversation
    let splitString = str.split("[INFO]");
    let returnStr = "\n";

    //parses each json line
    for (let i = 1; i < splitString.length; i++) {

        //parses role
        let roleList = splitString[i].split("'role': '")
        if (roleList.length == 1) {
            continue;
        }
        role = roleList[1].split("'")[0];
        role = role.toUpperCase();

        //parses content
        let content = splitString[i].split("'content': ")[1].slice(1, -2);
        content = content
            .replace(/\\n/g, "\n")

        //shouldn't render thought tags or test tags in these sections (only assistant)
        if (role == "USER" || role == "SYSTEM") {
            content = content
                .replace(/<test>/g, '[Test Tag]')
                .replace(/<\/test>/g, '[Test Tag]')
                .replace(/<thought>/g, '[Thought Tag]')
                .replace(/<\/thought>/g, '[Thought Tag]');
        }

        if (i == 1) {
            content = content
                .replace(/                /g, '')
                .replace(/\n/g, "\n\n")
                .replace(/<thought>/g, '[Thought Tag]');
        }


        returnStr += role + " : " + content + "\n\n\n";
    }
    return returnStr;
}

//loads the directory structure into the html
document.addEventListener('DOMContentLoaded', () => {
    fetch('output.json')
        .then(response => response.json())
        .then(data => {
            renderDirectoryStructure(data);
        })
        .catch(error => console.error('Error loading directory structure:', error));
});

//parses output.json and creates ul hierarchy
function createListElement(item, currentPath = '') {
    const li = document.createElement('li');
    const arrow = document.createElement('span');

    // Update the current path based on the item's name
    const newPath = currentPath ? `${currentPath}/${item.name}` : item.name;

    //recurses down the json to add children
    if (item.type === 'directory') {
        li.className = 'folder';
        arrow.textContent = ' ▲ '; // Upward arrow for collapsed state
        li.prepend(arrow); // Add arrow before the folder name
        li.appendChild(document.createTextNode(item.name)); // Append the folder name

        const ul = document.createElement('ul');
        ul.style.display = 'none'; // Initially hidden

        item.children.forEach(child => {
            ul.appendChild(createListElement(child, newPath)); // Pass the updated path
        });

        li.appendChild(ul);
        li.addEventListener('click', (event) => {
            if (event.target === li || event.target === arrow) {
                if (ul.style.display === 'none') {
                    ul.style.display = 'block'; // Show the children
                    arrow.textContent = ' ▼ '; // Change to downward arrow
                } else {
                    ul.style.display = 'none'; // Hide the children
                    arrow.textContent = ' ▲ '; // Change to upward arrow
                }
            }
            // if (ul.style.display === 'none') {
            //     ul.style.display = 'block'; // Show the children
            //     arrow.textContent = ' ▼ '; // Change to downward arrow
            // } else {
            //     ul.style.display = 'none'; // Hide the children
            //     arrow.textContent = ' ▲ '; // Change to upward arrow
            // }
            event.stopPropagation(); // Prevent the event from bubbling up
        });
    } else {
        //sets the onclick handlers of the files to load them
        li.className = 'file';
        li.textContent = item.name; // For files, just show the name
        if (item.name == 'conversations.jsonl') {
            console.log(newPath);

            li.addEventListener('click', () => {
                fetchJson(newPath);
            });


        } else {
            li.addEventListener('click', () => {
                console.log(`File clicked: ${newPath}`); // Log the path of the file
                //if adding the indicator for a successful run, add a class to the div corresponding to whatever element you want the indicator 
                //to be on and add some visual indication of that class in the css for it to show up in the directory structure.
                loadLog(newPath)
            });
        }
    }
    return li;
}

//calls load functions
function renderDirectoryStructure(directoryStructure) {
    const container = document.getElementById('sidebar');
    container.innerHTML = ''; // Clear previous content
    const ul = document.createElement('ul');

    // Start with the root structure
    //NOTE: IF YOU WANT TO CHANGE WHERE THE LOG FOLDER IS LOCATED IN THIS APPENDCHILD FUNCTION
    // CHANGE THE ".." TO THE RELATIVE PATH TO THE LOG FOLDER (EX: FOR ../../../common/log it would be ../../../common in this function)
    ul.appendChild(createListElement(directoryStructure.children[0], ".."));
    container.appendChild(ul);
}

//calls load json
function fetchJson(path) {
    fetch(path)
        .then(response => response.text())  // Read as text
        .then(text => {
            const lines = text.trim().split('\n');  // Split by newline
            const jsonData = lines.map(line => {
                try {
                    return JSON.parse(line);  // Parse each line
                } catch (e) {
                    console.error('Error parsing line:', line, e);
                    return null;  // Handle parsing error
                }
            }).filter(item => item !== null);  // Filter out invalid entries

            loadJson(jsonData);  // Pass the array of JSON objects to loadJson
        })
        .catch(error => console.error('Error loading conversation:', error));
}

//parses conversation.jsonl file using similar logic to parser
function loadJson(data) {
    const preElement = document.querySelector('#fileContent');
    preElement.innerHTML = '';
    data.forEach(elem => {
        const div = document.createElement('div');
        div.classList.add("convo")
        let role = elem.role.toUpperCase();
        let content = elem.content
            .replace(/\\n/g, "\n");
        if (role == "USER" || role == "SYSTEM") {
            content = content
                .replace(/<test>/g, '[Test Tag]')
                .replace(/<\/test>/g, '[Test Tag]')
                .replace(/<thought>/g, '[Thought Tag]')
                .replace(/<\/thought>/g, '[Thought Tag]');
        }

        if (role == "SYSTEM") {
            content = content
                .replace(/                /g, '')
                .replace(/\n/g, "\n\n")
                .replace(/<thought>/g, '[Thought Tag]');
        }
        divStuff = role + ": " + content + "\n\n\n";
        const pattern = /<test>(.*?)<\/test>/gs;
        const patternThought = /<thought>(.*?)<\/thought>/gs;
        div.innerHTML = divStuff
            .replace(pattern, (match, p1) => {
                return `<div class="highlight">
                                <div class = "highlight title"> GENERATED TEST CASE </div>
                                ${p1}
                            </div>`;

            })
            .replace(patternThought, (match, p1) => {
                return `<div class = "thought">
                                <div class = "convo title"> LLM THOUGHTS </div>    
                                ${p1}
                            </div>`
            });
        preElement.appendChild(div);

    });


}

// parses the larger log file
// **IDEA: to add a success failure visual feature, add a regex to check for the success tag and add a return value for the function
// see the onclick function in createListElement for more detail
function loadLog(fileUrl) {
    fetch(fileUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            const preElement = document.querySelector('#fileContent');

            //extracts the tests, conversations and thoughts using regex
            const pattern = /<test>(.*?)<\/test>/gs;
            const patternThought = /<thought>(.*?)<\/thought>/gs;
            const consolePattern = /\[CONVERSATION(\d+)\.JSONL\](.*?)\[\/CONVERSATION\.JSONL\]/gs;

            //replaces relavent portions of text with divs to add special classes to the extracted text
            preElement.innerHTML = data
                .replace(consolePattern, (match, iterationIndex, p1) => {
                    let parsed = parser(p1);
                    return `<div class="convo">
                                <div class="convo title"> CONVERSATION ${iterationIndex} </div>
                                ${parsed}
                            </div>`;
                })
                .replace(pattern, (match, p1) => {
                    return `<div class="highlight">
                                <div class = "highlight title"> GENERATED TEST CASE </div>
                                ${p1}
                            </div>`;

                })
                .replace(patternThought, (match, p1) => {
                    return `<div class = "thought">
                                <div class = "convo title"> LLM THOUGHTS </div>    
                                ${p1}
                            </div>`
                });
        })
        .catch(error => {
            console.error('There was a problem with fetch operation:', error);
        });
}
