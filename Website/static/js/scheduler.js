function ShowCourse(courseNum) {
    button = document.getElementById("course-form-" + courseNum);
    if (button.hasAttribute("hidden")) {
        button.removeAttribute("hidden");
    }
    else {
        button.setAttribute("hidden", true);
    }
}


function CourseOption(i) {

    var radios = document.querySelectorAll('input[type=radio][name="Core_Course_' + i + '"]');
    radios.forEach(radio => radio.addEventListener('change', () => {
        if (radio.value === "Core") {
            document.getElementById("core-course-form-" + i).removeAttribute("hidden");
            document.getElementById("normal-course-form-" + i).setAttribute("hidden", true)
            Clear(i, "Core");

        }
        else {
            document.getElementById("core-course-form-" + i).setAttribute("hidden", true);
            document.getElementById("normal-course-form-" + i).removeAttribute("hidden");
            Clear(i, "Normal");
        }
    }));

}

function ShowNextCourse(i, type) {
    const same = String(Number(i) - 1)
    buttonCourseDetail = document.getElementById("course-form-" + same);
    if (buttonCourseDetail.hasAttribute("hidden")) {
        buttonCourseDetail.removeAttribute("hidden");
    }
    else {
        buttonCourseDetail.setAttribute("hidden", true);
    }

    AddCourse = document.getElementById("AddCourse" + i);
    if (AddCourse.hasAttribute("hidden")) {
        AddCourse.removeAttribute("hidden");
    }

    AddCourse = document.getElementById("AddCourse" + same);
    if (type === "core") {
        AddCourse.textContent = `Course#${same} | ${document.getElementById("Core_Course" + same).value}`;
    }
    else {
        try {
            AddCourse.textContent = `Course#${same} | ${document.getElementById("Course_Name" + same).value} | ${document.getElementById("Instructor" + same).value} | ${document.getElementById("Section" + same).value}`;
        } catch (error) {
            try {
                AddCourse.textContent = `Course#${same} | ${document.getElementById("Course_Name" + same).value} | ${document.getElementById("Instructor" + same).value}`;
            } catch (error2) {
                AddCourse.textContent = `Course#${same} | ${document.getElementById("Course_Name" + same).value}`;
            }
        }

    }
}

function optionBuilder(data, id) {
    var dataList = document.getElementById(id);
    var option = document.createElement("option");
    option.value = data;
    dataList.appendChild(option);
}

async function CoursesAPI(i) {
    const department = document.getElementById("Department" + i).value;
    const courseNameInput = document.getElementById("Course_Name" + i);

    const HiddenCourseName = document.getElementById("Hcn" + i);
    const HiddenCRN = document.getElementById("CRNS" + i);
    const HiddenInstructor = document.getElementById("Hins" + i);
    const HiddenSection = document.getElementById("Hsec" + i);


    const response = await fetch(`/scheduler/courses/?department=${department}`);
    if (response.status === 200) {
        const data = await response.json();

        const courseNames = data.map(course => course.Title);
        const uniqueCourseNames = [...new Set(courseNames)];

        const CRNS = data.map(course => course.key);
        const instructors = data.map(course => course.Instructor);
        const times = data.map(course => course.Time);
        const days = data.map(course => course.Days);
        const sections = data.map(course => course.Section);

        const ShownSection = sections.map((element, index) => {
            return `Section ${element} ${days[index]} ${times[index]}`;
        });
        // CRNInput.setAttribute("value", CRNS.join("$$$$$$"));

        courseNameInput.disabled = false;
        courseNameInput.required = true;

        HiddenCRN.setAttribute("value", CRNS.join("$$$$$$"));
        HiddenCourseName.setAttribute("value", courseNames.join("$$$$$$"));
        HiddenInstructor.setAttribute("value", instructors.join("$$$$$$"));
        HiddenSection.setAttribute("value", ShownSection.join("$$$$$$"));
        // autocomplete(courseNameInput, uniqueCourseNames);

        for (index in uniqueCourseNames) {
            optionBuilder(uniqueCourseNames[index], "Course_Selector" + i);
        }
    } else {
        courseNameInput.disabled = true;
    }
};

async function CoreAPI(i) {
    const core = document.getElementById("Core_Course" + i).value;
    const courseNameInput = document.getElementById("Core_Course_Name" + i);
    response = await fetch(`/scheduler/core/?core=${core}`);
    if (response.status === 200) {
        const data = await response.json();
        const courseNames = data.map(course => course.Title);
        const crns = data.map(course => course.key);
        const instructors = data.map(course => course.Instructor);
        const sections = data.map(course => course.Section);

        const uniqueCourseNames = [...new Set(courseNames)];
        courseNameInput.disabled = false;
        courseNameInput.required = false;
        for (index in uniqueCourseNames) {
            optionBuilder(uniqueCourseNames[index], "Core_Course_Selector" + i);
        }

        const HiddenCRN = document.getElementById("CORE" + i);
        const HiddenCourseName = document.getElementById("Core_HCN" + i);
        const HiddenInstructor = document.getElementById("Core_Hins" + i);
        const HiddenSection = document.getElementById("Core_Hsec" + i);

        HiddenCRN.setAttribute("value", crns.join("$$$$$$"));
        HiddenCourseName.setAttribute("value", courseNames.join("$$$$$$"));
        HiddenInstructor.setAttribute("value", instructors.join("$$$$$$"));
        HiddenSection.setAttribute("value", sections.join("$$$$$$"));

    }

};

async function CoreCourseName(i) {
    const courseNameInput = document.getElementById("Core_Course_Name" + i);
    const HiddenCourseName = document.getElementById("Core_HCN" + i);
    const HiddenCRN = document.getElementById("CORE" + i);
    const HiddenInstructor = document.getElementById("Core_Hins" + i);
    const HiddenSection = document.getElementById("Core_Hsec" + i);

    const courseName = courseNameInput.value;
    const courseNames = HiddenCourseName.value.split("$$$$$$");
    const crns = HiddenCRN.value.split("$$$$$$");
    const instructors = HiddenInstructor.value.split("$$$$$$");
    const sections = HiddenSection.value.split("$$$$$$");

    const newCRNS = [];
    const newSections = [];
    const newInstructors = [];

    const InstructorSelector = document.getElementById("Core_Instructor" + i);
    InstructorSelector.disabled = false;

    const SectionSelector = document.getElementById("Core_Section" + i);
    SectionSelector.disabled = false;

    courseNames.forEach((element, index) => {
        if (element === courseName) {
            newCRNS.push(crns[index]);
            newSections.push(sections[index]);
            newInstructors.push(instructors[index]);
            optionBuilder(instructors[index], "Core_Instructor_Selector" + i);
            optionBuilder(sections[index], "Core_Section_Selector" + i);
        }
    });

    if (newSections.length >= 1) {
        HiddenCRN.setAttribute("value", newCRNS.join("$$$$$$"));
        HiddenInstructor.setAttribute("value", newInstructors.join("$$$$$$"));
        HiddenSection.setAttribute("value", newSections.join("$$$$$$"));
    }

};

function CoreInstructor(i) {
    const InstructorInput = document.getElementById("Core_Instructor" + i);
    const HiddenCourseName = document.getElementById("Core_HCN" + i);
    const HiddenCRN = document.getElementById("CORE" + i);
    const HiddenInstructor = document.getElementById("Core_Hins" + i);
    const HiddenSection = document.getElementById("Core_Hsec" + i);

    const instructor = InstructorInput.value;
    const courseNames = HiddenCourseName.value.split("$$$$$$");
    const crns = HiddenCRN.value.split("$$$$$$");
    const instructors = HiddenInstructor.value.split("$$$$$$");
    const sections = HiddenSection.value.split("$$$$$$");

    const newCRNS = [];
    const newSections = [];
    const newInstructors = [];
    const Section_Selector = document.getElementById("Core_Section_Selector" + i);

    instructors.forEach((element, index) => {
        if (element === instructor) {
            newCRNS.push(crns[index]);
            newSections.push(sections[index]);
            newInstructors.push(instructors[index]);
            Section_Selector.innerHTML = "";
            optionBuilder(sections[index], "Core_Section_Selector" + i);

        }

    });
    if (newSections.length >= 1) {
        HiddenCRN.setAttribute("value", newCRNS.join("$$$$$$"));
        HiddenInstructor.setAttribute("value", newInstructors.join("$$$$$$"));
        HiddenSection.setAttribute("value", newSections.join("$$$$$$"));
    }

};

function CoreSection(i) {

    const SectionInput = document.getElementById("Core_Section" + i);
    const HiddenCourseName = document.getElementById("Core_HCN" + i);
    const HiddenCRN = document.getElementById("CORE" + i);
    const HiddenInstructor = document.getElementById("Core_Hins" + i);
    const HiddenSection = document.getElementById("Core_Hsec" + i);

    const section = SectionInput.value;
    const courseNames = HiddenCourseName.value.split("$$$$$$");
    const crns = HiddenCRN.value.split("$$$$$$");
    const instructors = HiddenInstructor.value.split("$$$$$$");
    const sections = HiddenSection.value.split("$$$$$$");

    const newCRNS = [];
    const newSections = [];
    const newInstructors = [];

    sections.forEach((element, index) => {
        if (element === section) {
            newCRNS.push(crns[index]);
            newSections.push(sections[index]);
            newInstructors.push(instructors[index]);
        }
    });
}


function CourseNameSelector(i) {
    const InstructorInput = document.getElementById("Instructor" + i);
    const SectionInput = document.getElementById("Section" + i);

    const SelectedCourseName = document.getElementById("Course_Name" + i).value;
    // const instructor = InstructorInput.value;

    const HiddenCourseName = document.getElementById("Hcn" + i);
    const HiddenCRN = document.getElementById("CRNS" + i);
    const HiddenInstructor = document.getElementById("Hins" + i);
    const HiddenSection = document.getElementById("Hsec" + i);

    const CoursesNames = HiddenCourseName.value.split("$$$$$$");
    const CRNS = HiddenCRN.value.split("$$$$$$");
    const Instructors = HiddenInstructor.value.split("$$$$$$");
    const ShownSections = HiddenSection.value.split("$$$$$$");

    const newCRNS = [];
    const newSections = [];
    const newInstructors = [];

    CoursesNames.forEach((element, index) => {
        if (element === SelectedCourseName) {
            console.log(element, SelectedCourseName, CRNS[index]);
            newCRNS.push(CRNS[index]);
            newSections.push(ShownSections[index]);
            newInstructors.push(Instructors[index]);
            optionBuilder(ShownSections[index], "Section_Selector" + i);
        }
    });
    const inst_option = [...new Set(newInstructors)]
    for (index in inst_option) {
        optionBuilder(inst_option[index], "Instructor_Selector" + i);
    }

    if (newInstructors.length >= 1) {
        HiddenCRN.setAttribute("value", newCRNS.join("$$$$$$"));
        HiddenInstructor.setAttribute("value", newInstructors.join("$$$$$$"));
        HiddenSection.setAttribute("value", newSections.join("$$$$$$"));
        HiddenCourseName.setAttribute("value", SelectedCourseName);
        InstructorInput.disabled = false;
        SectionInput.disabled = false;
    }

};

function Instructor_Selector(i) {
    const InstructorInput = document.getElementById("Instructor" + i);
    // const SectionInput = document.getElementById("Section" + i);
    const SectionSelector = document.getElementById("Section_Selector" + i);
    // const SelectedCourseName = document.getElementById("Course_Name" + i).value;
    const instructor = InstructorInput.value;

    // const HiddenCourseName = document.getElementById("Hcn" + i);
    const HiddenCRN = document.getElementById("CRNS" + i);
    const HiddenInstructor = document.getElementById("Hins" + i);
    const HiddenSection = document.getElementById("Hsec" + i);

    // const CoursesNames = HiddenCourseName.value.split("$$$$$$");
    const CRNS = HiddenCRN.value.split("$$$$$$");
    const Instructors = HiddenInstructor.value.split("$$$$$$");
    const ShownSections = HiddenSection.value.split("$$$$$$");

    const newCRNS = [];
    const newSections = [];


    Instructors.forEach((element, index) => {
        if (element === instructor) {
            newCRNS.push(CRNS[index]);
            newSections.push(ShownSections[index]);
        }
    });

    if (newSections.length >= 1) {
        HiddenCRN.setAttribute("value", newCRNS.join("$$$$$$"));
        HiddenInstructor.setAttribute("value", instructor);
        HiddenSection.setAttribute("value", newSections.join("$$$$$$"));

        SectionSelector.innerHTML = "";

        for (index in newSections) {
            optionBuilder(newSections[index], "Section_Selector" + i);
        }
    }

};


function Section_Selector(i) {
    const InstructorInput = document.getElementById("Instructor" + i);
    const SectionInput = document.getElementById("Section" + i);
    const SectionSelector = document.getElementById("Section_Selector" + i);
    // const SelectedCourseName = document.getElementById("Course_Name" + i).value;
    const instructor = InstructorInput.value;

    // const HiddenCourseName = document.getElementById("Hcn" + i);
    const HiddenCRN = document.getElementById("CRNS" + i);
    const HiddenInstructor = document.getElementById("Hins" + i);
    const HiddenSection = document.getElementById("Hsec" + i);

    // const CoursesNames = HiddenCourseName.value.split("$$$$$$");
    const CRNS = HiddenCRN.value.split("$$$$$$");
    // const instructor = HiddenInstructor.value.split("$$$$$$");
    const ShownSections = HiddenSection.value.split("$$$$$$");


    ShownSections.forEach((element, index) => {
        if (element === SectionInput.value) {

            newCRNS = (CRNS[index]);
            newSections = (ShownSections[index]);

        }
    });

    if (newSections.length >= 1) {
        HiddenCRN.setAttribute("value", newCRNS);
        HiddenInstructor.setAttribute("value", instructor);
        HiddenSection.setAttribute("value", newSections);

        SectionSelector.innerHTML = "";

    }

};

function Clear(i, subj) {

    // Major Courses
    const InstructorInput = document.getElementById("Instructor" + i);
    const SectionInput = document.getElementById("Section" + i);
    const SectionSelector = document.getElementById("Section_Selector" + i);
    const CourseNameInput = document.getElementById("Course_Name" + i);
    const CourseSelector = document.getElementById("Course_Selector" + i);
    // const CoreSelector = document.getElementById("Core_Selector" + i);
    const DepartmentInput = document.getElementById("Department" + i);


    InstructorInput.value = "";
    SectionInput.value = "";
    SectionSelector.innerHTML = "";
    CourseNameInput.value = "";
    CourseSelector.innerHTML = "";
    // CoreSelector.innerHTML = "";
    DepartmentInput.value = "";

    // Core Courses
    const CoreInput = document.getElementById("Core_Course" + i);
    const CoreCourseNameInput = document.getElementById("Core_Course_Name" + i);
    const CoreInstructor = document.getElementById("Core_Instructor" + i);
    const CoreSection = document.getElementById("Core_Section" + i);
    const CoreCourseSelector = document.getElementById("Core_Course_Selector" + i);
    const CoreInstructorSelector = document.getElementById("Core_Instructor_Selector" + i);
    const CoreSectionSelector = document.getElementById("Core_Section_Selector" + i);

    CoreInput.value = "";
    CoreCourseNameInput.value = "";
    CoreInstructor.value = "";
    CoreSection.value = "";
    CoreCourseSelector.innerHTML = "";
    CoreInstructorSelector.innerHTML = "";
    CoreSectionSelector.innerHTML = "";


    // Hidden Values
    const HiddenCRN = document.getElementById("CRNS" + i);
    const HiddenInstructor = document.getElementById("Hins" + i);
    const HiddenSection = document.getElementById("Hsec" + i);
    const HiddenCourseName = document.getElementById("Hcn" + i);
    // const HiddenCore = document.getElementById("CORE" + i);

    HiddenCRN.setAttribute("value", "");
    HiddenInstructor.setAttribute("value", "");
    HiddenSection.setAttribute("value", "");
    HiddenCourseName.setAttribute("value", "");
    // HiddenCore.setAttribute("value", "");

    if (subj === "Core") {
        CourseNameInput.disabled = true;
        InstructorInput.disabled = true;
        SectionInput.disabled = true;
    } else {
        CourseNameInput.disabled = false;
        InstructorInput.disabled = true;
        SectionInput.disabled = true;
    }
}