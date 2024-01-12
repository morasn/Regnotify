async function CourseDetail(i) {
    var crn_input = document.getElementById('crn' + i);
    var crn = crn_input.value;
    var semester = document.getElementById('semester').value;
    var title = document.getElementById('title' + i);
    var section = document.getElementById('section' + i);
    var instructor = document.getElementById('instructor' + i);
    var card_header = document.getElementById('card-header' + i);

    title_label = document.getElementById('title-label' + i);
    section_label = document.getElementById('section-label' + i);
    instructor_label = document.getElementById('instructor-label' + i);

    // Check if the CRN is valid (5 digits)
    if (crn.length === 5) {
        // Send a GET request to the server to fetch course details
        const response = await fetch(`/add/crn/?crn=${crn}&semester=${semester}`);

        // If the response is successful (status code 200), update the HTML elements with the fetched data
        if (response.status === 200) {
            const data = await response.json();

            // Update the HTML elements with the fetched data
            title_label.textContent = "Title:";
            section_label.textContent = "Section:";
            instructor_label.textContent = "Instructor:";

            title.textContent = data["Title"];
            section.textContent = data["Section"];
            instructor.textContent = data["Instructor"];

            card_header.setAttribute("class", "card-header-accepted");

            // Hide the cards after the third one
            if (i >= 3 && i < 9) {
                var card = document.getElementById('card' + String(Number(i) + 1));
                card.removeAttribute("hidden");
            }

            // Enable the next card if the previous one succeeded
            if (i < 9) {
                var next_crn = document.getElementById('crn' + String(Number(i) + 1));
                next_crn.removeAttribute("disabled");
            }


        }
        // If the response is not successful, display an error message and highlight the CRN input element
        else {

            title_label.textContent = "Course not found";
            section_label.textContent = "";
            instructor_label.textContent = "";

            title.textContent = "";
            section.textContent = "";
            instructor.textContent = "";
            card_header.setAttribute("class", "card-header");
        };
    }
}
