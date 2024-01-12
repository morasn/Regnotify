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
	const prev = String(Number(i) - 1)
	buttonCourseDetail = document.getElementById("course-form-" + prev);
	buttonCourseDetail.setAttribute("hidden", true);

	AddCourse = document.getElementById("AddCourse" + i);
	if (AddCourse.hasAttribute("hidden")) {
		AddCourse.removeAttribute("hidden");
	}

	AddCourse = document.getElementById("AddCourse" + prev);
	if (type === "core") {
		AddCourse.textContent = `Course#${prev} | ${document.getElementById("Core_Course" + prev).value}`;
	}
	else {
		AddCourse.textContent = `Course#${prev} | ${document.getElementById("Course_Name" + prev).value}`;
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
			const courseNames = JSON.parse(localStorage.getItem(`CourseNames-${department.replace(/&/g, "----")}`));
			const uniqueCourseNames = [...new Set(courseNames)];

			for (index in uniqueCourseNames) {
				optionBuilder(uniqueCourseNames[index], "Course_Selector" + i);
			}
		};
	} else {
		const response = await fetch(`/scheduler/courses/?department=${department.replace(/&/g, "----")}&semester=${semester}`);
		if (response.status === 200) {
			const data = await response.json();

			const courseNames = data.map(course => course.Title);
			const CRNS = data.map(course => course.key);
			const instructors = data.map(course => course.Instructor);
			const times = data.map(course => course.Time);
			const days = data.map(course => course.Days);
			const sections = data.map(course => course.Section);
			const CourseID = data.map(course => course.Course_ID);

			const ShownSection = sections.map((element, index) => {
				return `Section ${element} ${days[index]} ${times[index]}`;
			});
			const ShownCourseName = courseNames.map((element, index) => {
				return `${element} - ${CourseID[index]}`;
			});
			const uniqueCourseNames = [...new Set(ShownCourseName)];

			courseNameInput.disabled = false;
			courseNameInput.required = true;

			HiddenCRN.setAttribute("value", JSON.stringify(CRNS));

			localStorage.setItem(`CRNS-${department}`, JSON.stringify(CRNS));
			localStorage.setItem(`CourseNames-${department}`, JSON.stringify(ShownCourseName));
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

function SaveAPI(data, i, core, courseNameInput) {
	const courseNames = data.map(course => course.Title);
	const CRNS = data.map(course => course.key);
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
	const HiddenCRN = document.getElementById("CRNS" + i);

	HiddenCRN.setAttribute("value", JSON.stringify(CRNS));

	const now = new Date();

	localStorage.setItem(`CRNS-${core}`, JSON.stringify(CRNS));
	localStorage.setItem(`CourseNames-${core}`, JSON.stringify(courseNames));
	localStorage.setItem(`Instructors-${core}`, JSON.stringify(instructors));
	localStorage.setItem(`Sections-${core}`, JSON.stringify(ShownSection));
	localStorage.setItem(`time-${core}`, JSON.stringify(now.getTime())); // store time of localStorage update

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
		response = await fetch(`/scheduler/core/?core=${core.replace(/&/g, "----")}&semester=${semester}`);
		if (response.status === 200 && core !== "RHET 1010 & Core 1010") {
			const data = await response.json();
			const list1 = data[0];
			SaveAPI(list1, i, core, courseNameInput)
			// const courseNames = data.map(course => course.Title);
			// const CRNS = data.map(course => course.key);
			// const instructors = data.map(course => course.Instructor);
			// const sections = data.map(course => course.Section);
			// const times = data.map(course => course.Time);
			// const days = data.map(course => course.Days);

			// const uniqueCourseNames = [...new Set(courseNames)];
			// courseNameInput.disabled = false;
			// courseNameInput.required = false;

			// for (index in uniqueCourseNames) {
			// 	optionBuilder(uniqueCourseNames[index], "Core_Course_Selector" + i);
			// }

			// const ShownSection = sections.map((element, index) => {
			// 	return `Section ${element} ${days[index]} ${times[index]}`;
			// });
			// const HiddenCRN = document.getElementById("CRNS" + i);

			// HiddenCRN.setAttribute("value", JSON.stringify(CRNS));

			// localStorage.setItem(`CRNS-${core}`, JSON.stringify(CRNS));
			// localStorage.setItem(`CourseNames-${core}`, JSON.stringify(courseNames));
			// localStorage.setItem(`Instructors-${core}`, JSON.stringify(instructors));
			// localStorage.setItem(`Sections-${core}`, JSON.stringify(ShownSection));
			// localStorage.setItem(`time-${core}`, JSON.stringify(now.getTime())); // store time of localStorage update

		}
		if (core === "RHET 1010 & Core 1010" && response.status === 200) {
			const data = await response.json();

			// Assuming the API response is an object with two properties: list1 and list2
			const list1 = data[0];
			SaveAPI(list1, i, core, courseNameInput)
			const list2 = data[1];
			SaveAPI(list2, 11, core, courseNameInput)

		}
	}

};


function FormControl(i, level, type) { // if level = 1: CourseName; if level = 2: instructor; if level = 3: section
	Clear(i, level + 1);

	let Department, CourseName, Instructor, Section;
	const HiddenCRN = document.getElementById("CRNS" + i);
	if (type === 'core') {
		// Core Courses
		Department = document.getElementById("Core_Course" + i);
		CourseName = document.getElementById("Core_Course_Name" + i);
		Instructor = document.getElementById("Core_Instructor" + i);
		Section = document.getElementById("Core_Section" + i);

	} else {
		// Major Courses
		Department = document.getElementById("Department" + i);
		CourseName = document.getElementById("Course_Name" + i);
		Instructor = document.getElementById("Instructor" + i);
		Section = document.getElementById("Section" + i);
	};

	const CRNS = JSON.parse(localStorage.getItem(`CRNS-${Department.value}`));
	const CourseNames = JSON.parse(localStorage.getItem(`CourseNames-${Department.value}`));
	const Instructors = JSON.parse(localStorage.getItem(`Instructors-${Department.value}`));
	const Sections = JSON.parse(localStorage.getItem(`Sections-${Department.value}`));

	if (level !== 3) {
		const newCRNS = [];
		const newSections = [];
		const newInstructors = [];

		if (level === 1) {
			CourseNames.forEach((element, index) => {
				if (element === CourseName.value) {
					newCRNS.push(CRNS[index]);
					newSections.push(Sections[index]);
					newInstructors.push(Instructors[index]);
					optionBuilder(Sections[index], "Section_Selector" + i)
				}
			});
			const inst_option = [...new Set(newInstructors)]
			for (index in inst_option) {
				optionBuilder(inst_option[index], "Instructor_Selector" + i);
			}

			if (newInstructors.length >= 1) {
				HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
				Instructor.disabled = false;
				Section.disabled = false;
			}

		}


		if (level === 2) {
			Instructors.forEach((element, index) => {
				if (element === Instructor.value && CourseNames[index] === CourseName.value) {
					newCRNS.push(CRNS[index]);
					newSections.push(Sections[index]);

					optionBuilder(Sections[index], "Section_Selector" + i);
				}
			});
			if (newSections.length >= 1) {
				HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
			}
		}


	}

	if (level === 3) {
		let newCRNS = false;
		Sections.forEach((element, index) => {
			if (element === Section.value && CourseNames[index] === CourseName.value) {
				newCRNS = String(CRNS[index]);
			}
		});
		if (newCRNS !== false) {
			HiddenCRN.setAttribute("value", JSON.stringify(newCRNS));
		}
	};

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
	const CoreInstructorSelector = document.getElementById("Instructor_Selector" + i);
	const CoreSectionSelector = document.getElementById("Section_Selector" + i);
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
		CoreInstructor.disabled = true;
		CoreSection.disabled = true;

	}
	if (level <= 0) {
		DepartmentInput.value = "";
		CoreInput.value = "";

		CourseNameInput.disabled = true;
		CoreCourseNameInput.disabled = true;

		const HiddenCRN = document.getElementById("CRNS" + i);
		HiddenCRN.setAttribute("value", "");
	}

}
