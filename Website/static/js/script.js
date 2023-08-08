const OTPinputs = document.querySelectorAll("input");
const button = document.querySelector("button");

window.addEventListener("load", () => OTPinputs[0].focus());

OTPinputs.forEach((input) => {
    input.addEventListener("input", () => {
        const currentInput = input;
        const nextInput = input.nextElementSibling;

        if (currentInput.value.length > 1 && currentInput.value.length == 2) {
            currentInput.value = "";
        }

        if (nextInput !== null && nextInput.hasAttribute("disabled") && currentInput.value !== "") {
            nextInput.removeAttribute("disabled");
            nextInput.focus();
        }

        if (!OTPinputs[3].disabled && OTPinputs[3].value !== "") {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }

    });


    input.addEventListener("keyup", (e) => {
        if (e.key === "Backspace") {
            if (input.previousElementSibling !== null) {
                e.target.value = "";
                e.target.setAttribute("disabled", true);
                input.previousElementSibling.focus();
            }
        }
    })

});



// button.addEventListener("click", async () => {
//     // Get the OTP from the input fields.

//     const OTPinputs = [
//         document.getElementById("otp1"),
//         document.getElementById("otp2"),
//         document.getElementById("otp3"),
//         document.getElementById("otp4"),
//     ];
//     const otp = OTPinputs.map((input) => input.value).join("");
    
//     // const data = await response.json();

//     // if (response.status === 200 && data.auth === true) {
//     //     window.location.href = "loginOLD.html";
//     // } else {
//     //     alert("Invalid OTP");
//     // }
// });


