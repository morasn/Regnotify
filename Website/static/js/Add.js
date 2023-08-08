async function CourseDetail(i) {
    var crn_input = document.getElementById('crn' + i);
    var crn = crn_input.value;
    var semester = document.getElementById('semester').value;
    var course_detail = document.getElementById('crn_detail' + i);
    if (crn.length === 5) {
        const response = await fetch(`/add/crn/?crn=${crn}&semester=${semester}`);
        if (response.status === 200) {
            const data = await response.text();

            course_detail.textContent = data;
            crn_input.setAttribute("class", "search__input");
        }
        else {
            course_detail.textContent = "Course not found";
            crn_input.setAttribute("class", "search__input_error");
        }
    }
}