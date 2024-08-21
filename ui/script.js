function parser(str) {
    let splitString = str.split("[INFO]");
    let returnStr = "\n";
    for (let i = 1; i < splitString.length; i++) {
        console.log(splitString[i]);
        let roleList = splitString[i].split("'role': '")
        if (roleList.length == 1) {
            continue;
        }
        role = roleList[1].split("'")[0];
        role = role.toUpperCase();
        let content = splitString[i].split("'content': ")[1].slice(1, -2);
        content = content
            .replace(/\\n/g, "\n")
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

document.addEventListener('DOMContentLoaded', () => {
    // Assuming your text file is named 'example.txt' and is in the same directory as your HTML file.
    const fileUrl = '../log/log_cve-2022-25173_2024-07-11 23:38:25.txt';
    let rawData = ""
    fetch(fileUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            const preElement = document.querySelector('#fileContent');
            //const pattern = /<test>((?!\[CONVERSATION\.JSONL\])(?:(?!\[\/CONVERSATION\.JSONL\]).)*)<\/test>/gs;
            //const pattern = /<\/CONVERSATION\.JSONL>\s*(?:[^<]*\n){0,2}<test>((?:(?!<test>|<\/test>|\[CONVERSATION\.JSONL\]).)*)<\/test>/gs;
            // Directly set the innerHTML to include the span tags
            const pattern = /<test>(.*?)<\/test>/gs;
            const patternThought = /<thought>(.*?)<\/thought>/gs;
            const regex2 = /(?:(?!\[CONVERSATION\.JSONL\]).)*?(?!\[\/CONVERSATION\.JSONL\])/gs;
            const consolePattern = /\[CONVERSATION\.JSONL\](.*?)\[\/CONVERSATION\.JSONL\]/gs;
            preElement.innerHTML = data
                .replace(consolePattern, (match, p1) => {
                    let parsed = parser(p1);
                    return `<div class = "convo">
                                <div class = "convo title"> CONVERSATION </div>
                                ${parsed}
                            </div>`
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
});


