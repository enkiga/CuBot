function inputValidator() {
    // Personal Details
    const fullName = document.getElementById("full-name").value.trim();
    const dob = document.getElementById("dob").value.trim();
    const mobileNo = document.getElementById("mobileNo").value.trim();

    // Education Details
    const campus = document.getElementById("campus").value.trim();
    const faculty = document.getElementById("faculty").value.trim();
    const program = document.getElementById("program").value.trim();
    const email = document.getElementById("email").value.trim();
    const studentID = document.getElementById("studentID").value.trim();
    const joinDate = document.getElementById("join-date").value.trim();

    // Authentication Details
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/;

    // Recovery Details
    const question = document.getElementById("question").value.trim();
    const answer = document.getElementById("answer").value.trim();


    // Validation logic goes here
    // Example: Check if the fullName field is empty
    if (fullName === "") {
        alert("Please enter your full name.");
        return false; // Prevent form submission
    }
    if (dob === "") {
        alert("Please enter your date of birth.");
        return false; // Prevent form submission
    }
    if (mobileNo === "") {
        alert("Please enter your mobile number.");
        return false; // Prevent form submission
    }
    if (!mobileNo.startsWith("+254")) {
        alert("Mobile number must start with +254");
        return false;
    }
    if (mobileNo.length !== 13) {
        alert("Mobile number must be 13 characters long");
        return false;
    }
    if (campus === "") {
        alert("Please enter your campus.");
        return false; // Prevent form submission
    }
    if (faculty === "") {
        alert("Please enter your faculty.");
        return false; // Prevent form submission
    }
    if (program === "") {
        alert("Please enter your program.");
        return false; // Prevent form submission
    }
    if (email === "") {
        alert("Please enter your email.");
        return false; // Prevent form submission
    }
    if (!email.endsWith("@cuea.edu")) {
        alert("Please enter a valid school email address");
        return false;
    }
    if (studentID === "") {
        alert("Please enter your student ID.");
        return false; // Prevent form submission
    }
    if (studentID.length !== 7) {
        alert("Student ID must be 7 characters long");
        return false;
    }
    if (joinDate === "") {
        alert("Please enter your join date.");
        return false; // Prevent form submission
    }

    if (password === "") {
        alert("Please enter your password.");
        return false; // Prevent form submission
    }
    if (confirmPassword === "") {
        alert("Please enter your confirm password.");
        return false; // Prevent form submission
    }
    if (!pattern.test(password)) {
        alert("Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (@$!%*?&), and must be at least 8 characters long");
        return false;
    }
    if (password !== confirmPassword) {
        alert("Password and confirm password must match");
        return false;
    }
    if (question === "") {
        alert("Please enter your question.");
        return false; // Prevent form submission
    }
    if (answer === "") {
        alert("Please enter your answer.");
        return false; // Prevent form submission
    }

    // If all validations pass, the form can be submitted
    return true;
}

function eventValidator() {
    // Event Details
    const eventName = document.getElementById("event-name").value.trim();
    const eventDate = document.getElementById("event-date").value.trim();
    const startTime = document.getElementById("start-time").value.trim();
    const stopTime = document.getElementById("stop-time").value.trim();
    const eventVenue = document.getElementById("venue").value.trim();
    const eventDescription = document.getElementById("event-description").value.trim();
    const campus = document.getElementById("campus").value.trim();


    // Validation logic goes here
    // Example: Check if the fullName field is empty
    if (eventName === "") {
        alert("Please enter the event name.");
        return false; // Prevent form submission
    }
    if (eventDate === "") {
        alert("Please enter the event date.");
        return false; // Prevent form submission
    }
    if (startTime === "") {
        alert("Please enter the start time.");
        return false; // Prevent form submission
    }
    if (stopTime === "") {
        alert("Please enter the stop time.");
        return false; // Prevent form submission
    }
    if (eventVenue === "") {
        alert("Please enter the event venue.");
        return false; // Prevent form submission
    }
    if (eventDescription === "") {
        alert("Please enter the event description.");
        return false; // Prevent form submission
    }
    if (campus === "") {
        alert("Please select campus.");
        return false; // Prevent form submission
    }

    // If all validations pass, the form can be submitted
    return true;
}
