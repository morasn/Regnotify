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
			Clear(i, 0);

		}
		else {
			document.getElementById("core-course-form-" + i).setAttribute("hidden", true);
			document.getElementById("normal-course-form-" + i).removeAttribute("hidden");
			Clear(i, 0);
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

	Clear(i, 1);

	const department = document.getElementById("Department" + i).value;

	semester = document.getElementById("Semester").value;

	const courseNameInput = document.getElementById("Course_Name" + i);
	const HiddenCRN = document.getElementById("CRNS" + i);

	const oldTime = JSON.parse(localStorage.getItem(`time${department.replace(/&/g, "----")}`));
	const now = new Date();
	if (oldTime) {
		if (now.getTime() - oldTime < 60 * 60 * 6) {
			const courseNames = JSON.parse(localStorage.getItem(`CourseNames-${department}`));
			const uniqueCourseNames = [...new Set(courseNames)];

			for (index in uniqueCourseNames) {
				optionBuilder(uniqueCourseNames[index], "Course_Selector" + i);
			}
		};
	} else {
		const response = await fetch(`/scheduler/courses/?department=${department}&semester=${semester}`);
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

			courseNameInput.disabled = false;
			courseNameInput.required = true;

			HiddenCRN.setAttribute("value", JSON.stringify(CRNS));

			localStorage.setItem(`CRNS-${department}`, JSON.stringify(CRNS));
			localStorage.setItem(`CourseNames-${department}`, JSON.stringify(courseNames));
			localStorage.setItem(`Instructors-${department}`, JSON.stringify(instructors));
			localStorage.setItem(`Sections-${department}`, JSON.stringify(ShownSection));
			localStorage.setItem(`time-${department}`, JSON.stringify(now.getTime())); // store time of localStorage update

			for (index in uniqueCourseNames) {
				optionBuilder(uniqueCourseNames[index], "Course_Selector" + i);
			}
		} else {
			courseNameInput.disabled = true;
		}
	}
};


function CourseNameSelector(i) {

	Clear(i, 2);

	const department = document.getElementById("Department" + i).value;
	const SelectedCourseName = document.getElementById("Course_Name" + i).value;

	const InstructorInput = document.getElementById("Instructor" + i);
	const SectionInput = document.getElementById("Section" + i);

	const HiddenCRN = document.getElementById("CRNS" + i);

	const CoursesNames = JSON.parse(localStorage.getItem(`CourseNames-${department}`));
	const CRNS = JSON.parse(localStorage.getItem(`CRNS-${department}`));
	const Instructors = JSON.parse(localStorage.getItem(`Instructors-${department}`));
	const sections = JSON.parse(localStorage.getItem(`Sections-${department}`));

	const newCRNS = [];
	const newSections = [];
	const newInstructors = [];

	CoursesNames.forEach((element, index) => {
		if (element === SelectedCourseName) {
			newCRNS.push(CRNS[index]);
			newSections.push(sections[index]);
			newInstructors.push(Instructors[index]);
			optionBuilder(sections[index], "Section_Selector" + i)
		}
	});

	const inst_option = [...new Set(newInstructors)]
	for (index in inst_option) {
		optionBuilder(inst_option[index], "Instructor_Selector" + i);
	}

	if (newInstructors.length >= 1) {
		HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
		InstructorInput.disabled = false;
		SectionInput.disabled = false;
	}

};

function Instructor_Selector(i) {

	Clear(i, 3);

	const department = document.getElementById("Department" + i).value;
	const courseName = document.getElementById("Course_Name" + i).value;
	const InstructorInput = document.getElementById("Instructor" + i);
	const SectionSelector = document.getElementById("Section_Selector" + i);
	const instructor = InstructorInput.value;

	const HiddenCRN = document.getElementById("CRNS" + i);


	const CoursesNames = JSON.parse(localStorage.getItem(`CourseNames-${department}`));
	const CRNS = JSON.parse(localStorage.getItem(`CRNS-${department}`));
	const Instructors = JSON.parse(localStorage.getItem(`Instructors-${department}`));
	const sections = JSON.parse(localStorage.getItem(`Sections-${department}`));

	const newCRNS = [];
	const newSections = [];


	Instructors.forEach((element, index) => {
		if (element === instructor && CoursesNames[index] === courseName) {
			newCRNS.push(CRNS[index]);
			newSections.push(sections[index]);

			optionBuilder(sections[index], "Section_Selector" + i);
		}
	});

	if (newSections.length >= 1) {
		HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));

		// for (index in newSections) {
		// 	optionBuilder(newSections[index], "Section_Selector" + i);
		// }
	}

};


function Section_Selector(i) {
	const department = document.getElementById("Department" + i).value;
	const courseNameInput = document.getElementById("Course_Name" + i).value;
	const SectionInput = document.getElementById("Section" + i).value;

	const HiddenCRN = document.getElementById("CRNS" + i);

	const courseNames = JSON.parse(localStorage.getItem(`CourseNames-${department}`));
	const CRNS = JSON.parse(localStorage.getItem(`CRNS-${department}`));
	const sections = JSON.parse(localStorage.getItem(`Sections-${department}`));

	let newCRN = false;

	sections.forEach((element, index) => {
		if (element === SectionInput && courseNames[index] === courseNameInput) {
			newCRN = String(CRNS[index]);
		}
	});

	if (newCRN !== false) {
		HiddenCRN.setAttribute("value", JSON.stringify(newCRN));
	}
}

async function CoreAPI(i) {

	Clear(i, 1);

	const core = document.getElementById("Core_Course" + i).value;
	const courseNameInput = document.getElementById("Core_Course_Name" + i);
	const semester = document.getElementById("Semester").value;


	const oldTime = JSON.parse(localStorage.getItem(`time${core}`));
	const now = new Date();
	if (oldTime) {
		if (now.getTime() - oldTime < 60 * 60 * 6) {
			const courseNames = JSON.parse(localStorage.getItem(`CoreCourseNames-${core}`));
			const uniqueCourseNames = [...new Set(courseNames)];

			for (index in uniqueCourseNames) {
				optionBuilder(uniqueCourseNames[index], "Core_Course_Selector" + i);
			}
		};
	} else {
		response = await fetch(`/scheduler/core/?core=${core}&semester=${semester}`);
		if (response.status === 200) {
			const data = await response.json();
			const courseNames = data.map(course => course.Title);
			const crns = data.map(course => course.key);
			const instructors = data.map(course => course.Instructor);
			const sections = data.map(course => course.Section);
			const times = data.map(course => course.Time);
			const days = data.map(course => course.Days);

			const uniqueCourseNames = [...new Set(courseNames)];
			courseNameInput.disabled = false;
			courseNameInput.required = false;

			for (index in uniqueCourseNames) {
				optionBuilder(uniqueCourseNames[index], "Core_Course_Selector" + i);
			}

			const ShownSection = sections.map((element, index) => {
				return `Section ${element} ${days[index]} ${times[index]}`;
			});
			const HiddenCRN = document.getElementById("CORE" + i);

			HiddenCRN.setAttribute("value", JSON.stringify(crns));

			localStorage.setItem(`CRNS-${core}`, JSON.stringify(crns));
			localStorage.setItem(`CoreCourseNames-${core}`, JSON.stringify(courseNames));
			localStorage.setItem(`Instructors-${core}`, JSON.stringify(instructors));
			localStorage.setItem(`Sections-${core}`, JSON.stringify(ShownSection));
			localStorage.setItem(`time-${department}`, JSON.stringify(now.getTime())); // store time of localStorage update
		}
	}

};

async function CoreCourseName(i) {
	Clear(i, 2);

	const core = document.getElementById("Core_Course" + i).value;
	const courseNameInput = document.getElementById("Core_Course_Name" + i);
	const HiddenCRN = document.getElementById("CORE" + i);

	const courseName = courseNameInput.value;
	const courseNames = JSON.parse(localStorage.getItem(`CoreCourseNames-${core}`));
	const crns = JSON.parse(localStorage.getItem(`CRNS-${core}`));
	const instructors = JSON.parse(localStorage.getItem(`Instructors-${core}`));
	const sections = JSON.parse(localStorage.getItem(`Sections-${core}`));

	const newCRNS = [];
	const newSections = [];
	const newInstructors = [];

	const InstructorSelector = document.getElementById("Core_Instructor" + i);
	const SectionSelector = document.getElementById("Core_Section" + i);

	courseNames.forEach((element, index) => {
		if (element === courseName) {
			newCRNS.push(crns[index]);
			newSections.push(sections[index]);
			newInstructors.push(instructors[index]);
			optionBuilder(sections[index], "Core_Section_Selector" + i);
		}
	});

	const uniqueInstructors = [...new Set(newInstructors)];

	for (index in uniqueInstructors) {
		optionBuilder(uniqueInstructors[index], "Core_Instructor_Selector" + i);
	};


	if (newSections.length >= 1) {
		HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
		InstructorSelector.disabled = false;
		SectionSelector.disabled = false;
	}


};

function CoreInstructor(i) {
	Clear(i, 3);
	const core = document.getElementById("Core_Course" + i).value;
	const InstructorInput = document.getElementById("Core_Instructor" + i);
	const courseNameInput = document.getElementById("Core_Course_Name" + i);
	const HiddenCRN = document.getElementById("CORE" + i);

	const instructor = InstructorInput.value;
	const courseNames = JSON.parse(localStorage.getItem(`CoreCourseNames-${core}`));
	const crns = JSON.parse(localStorage.getItem(`CRNS-${core}`));
	const instructors = JSON.parse(localStorage.getItem(`Instructors-${core}`));
	const sections = JSON.parse(localStorage.getItem(`Sections-${core}`));

	const newCRNS = [];
	const newSections = [];


	const courseName = courseNameInput.value;
	instructors.forEach((element, index) => {
		if (element === instructor && courseNames[index] === courseName) {
			newCRNS.push(crns[index]);
			newSections.push(sections[index]);

			optionBuilder(sections[index], "Core_Section_Selector" + i);
		}

	});
	if (newSections.length >= 1) {
		HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
	}

};

function CoreSection(i) {
	const core = document.getElementById("Core_Course" + i).value;
	const SectionInput = document.getElementById("Core_Section" + i);
	const courseName = document.getElementById("Core_Course_Name" + i).value;
	const HiddenCRN = document.getElementById("CORE" + i);

	const courseNames = JSON.parse(localStorage.getItem(`CoreCourseNames-${core}`));
	const section = SectionInput.value;
	const crns = JSON.parse(localStorage.getItem(`CRNS-${core}`));
	const sections = JSON.parse(localStorage.getItem(`Sections-${core}`));

	let newCRNS = false;

	sections.forEach((element, index) => {
		if (element === section && courseNames[index] === courseName) {
			newCRNS = String(crns[index]);
		}
	});
	if (newCRNS !== false) {
		HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
	}
}

function Clear(i, level) { // if level = 0, clear all, if level = 1, CourseName, clear instructor and section, if level = 2, clear section, instructor, if level = 3, clear section

	// Major Courses
	const InstructorInput = document.getElementById("Instructor" + i);
	const SectionInput = document.getElementById("Section" + i);
	const SectionSelector = document.getElementById("Section_Selector" + i);
	const CourseNameInput = document.getElementById("Course_Name" + i);
	const CourseSelector = document.getElementById("Course_Selector" + i);
	const DepartmentInput = document.getElementById("Department" + i);
	const Instructor_Selector = document.getElementById("Instructor_Selector" + i);

	// Core Courses
	const CoreInput = document.getElementById("Core_Course" + i);
	const CoreCourseNameInput = document.getElementById("Core_Course_Name" + i);
	const CoreInstructor = document.getElementById("Core_Instructor" + i);
	const CoreSection = document.getElementById("Core_Section" + i);
	const CoreCourseSelector = document.getElementById("Core_Course_Selector" + i);
	const CoreInstructorSelector = document.getElementById("Core_Instructor_Selector" + i);
	const CoreSectionSelector = document.getElementById("Core_Section_Selector" + i);
	if (level <= 3) {
		SectionInput.value = "";
		SectionSelector.innerHTML = "";

		CoreSection.value = "";
		CoreSectionSelector.innerHTML = "";
	}
	if (level <= 2) {
		InstructorInput.value = "";
		Instructor_Selector.innerHTML = "";

		CoreInstructor.value = "";
		CoreInstructorSelector.innerHTML = "";
	}
	if (level <= 1) {
		CourseNameInput.value = "";
		CourseSelector.innerHTML = "";

		CoreCourseNameInput.value = "";
		CoreCourseSelector.innerHTML = "";

		InstructorInput.disabled = true;
		SectionInput.disabled = true;
	}
	if (level <= 0) {
		DepartmentInput.value = "";
		CoreInput.value = "";

		CourseNameInput.disabled = true;

		const HiddenCRN = document.getElementById("CRNS" + i);
		HiddenCRN.setAttribute("value", "");
	}

}
