function callDataFunction(data) {
    
    document.getElementById("submit").style.visibility = "hidden";
    const questionSet = new Set();
    questionSet.add("select");
    questionSet.add("text");


    // generate a question object constructor (created the type of question below)
    function Question(options, question) {
        this.options = options;
        this.question = question;
        this.textbox = document.createElement("input");
        this.date = document.createElement("input");
        this.optionInput = null;
        this.optionLabel = null;
    }
    // prototype of radio questions
    Question.prototype.createRadios = function() {
        // displaying radio buttons + options for each "select" type question
        let optionCount = 0;
        for (let eachOption in this.options){
            this.optionInput = document.createElement("input");
            this.optionLabel = document.createElement('label');
            this.optionInput.setAttribute("type", "radio");
            this.optionInput.setAttribute("name", "question" + String(count))
            this.optionInput.setAttribute("id", "question" + String(count) + "option" + String(optionCount));
            this.optionInput.setAttribute("value", this.options[eachOption].value);
            this.optionInput.className = "radioButtons";
            this.optionLabel.setAttribute('for', "question" + String(count) + "option" + String(optionCount));
            this.optionLabel.innerHTML = this.options[eachOption].label;
            this.question.appendChild(this.optionInput);
            this.question.appendChild(this.optionLabel);
            optionCount++;
        }
    }

    // prototype of textarea questions
    Question.prototype.createText = function() {
        // currently using textareas for each "text" type question
        this.textbox.className = "questionInput";
        this.textbox.setAttribute("type", "text");
        this.textbox.setAttribute("name", "answer");
        this.question.appendChild(this.textbox);
    }

    // prototype of textarea questions
    Question.prototype.createDate = function() {
        // currently using textareas for each "text" type question
        this.date.className = "questionInput";
        this.date.setAttribute("type", "date");
        this.date.setAttribute("placeholder", "yyyy-mm-dd");
        this.date.setAttribute("name", "answer");
        this.question.appendChild(this.date);
    }


    let questionIndex = 0;
    let count = 0;
    let questionsContainer = document.getElementById('questionsContainer');
    for (let each in data.document.content){
        let question = document.createElement("div");
        question.className = "questionDiv";
        question.style.display = "none";
        question.id = "question" + String(count);
        
        let questionHeader = document.createElement("P");
        let questionHeaderContent = document.createTextNode((parseInt(each) + 1) + ")  " + data.document.content[each].label);
        questionHeader.className = "questionText";   // Class for styling
        questionHeader.appendChild(questionHeaderContent);
        question.appendChild(questionHeader);
        let option = new Question(data.document.content[each].input.options, question);

        if (data.document.content[each].input.type === "select"){  // displaying questions that are type select
            question.className += " questionRadioDiv";
            option.createRadios();
        }
        else if (data.document.content[each].input.type === "text") {  // diplaying questions that are type text
            // currently using textareas for each "text" type question
            option.createText();
        }
        else if (data.document.content[each].input.type === "date") {
            option.createDate();
        }
                
        questionsContainer.appendChild(question);

        count++;
    }

    showIndexedQuestion();
    updateProgressBar();

    function updateProgressBar() {
        document.getElementById("progressBarFill").setAttribute("width", String(60 * (questionIndex + 1) / count) + "%");
    }

    function showIndexedQuestion() {
        console.log("Tried to show index " + questionIndex);
        document.getElementById("question" + String(questionIndex)).style.display = "block"; // Show question div.
    }

    function hideIndexedQuestion() {
        document.getElementById("question" + String(questionIndex)).style.display = "none"; // Hides question div.
    }


    function back() {
        let submit = document.getElementById("submit");
        submit.style.visibility="hidden";
        if (questionIndex == 0) {
            console.log("Can't go back");
        } else {
            hideIndexedQuestion();
            questionIndex--;
            showIndexedQuestion();

            updateProgressBar();
        }
    }

    function forward() {
        if (questionIndex == data.document.content.length - 1) {
            let submit = document.getElementById("submit");
            submit.style.visibility="visible";
            console.log("Can't go Forward");
        } else {
            hideIndexedQuestion();
            questionIndex++;
            showIndexedQuestion();

            updateProgressBar();
        }
    }

    let backArrow = document.getElementById("backArrow");
    let frontArrow = document.getElementById("frontArrow");
    backArrow.onclick = back;
    frontArrow.onclick = forward;
}