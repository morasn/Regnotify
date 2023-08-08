
function showSchedule(current, next) {
    Current_table = document.getElementById("Schedule" + current);
    Next_table = document.getElementById("Schedule" + next);
    // try {
    //     Current_table.setAttribute("hidden", true);
    //     Next_table.removeAttribute("hidden");
    // }
    // catch (err) {
    //     console.log(err);
    // }
    Current_table.setAttribute("class", "none");
    Next_table.setAttribute("class", "container");
}

// function DownloadSchedule(id) {
//     var doc = new jspdf.jsPDF('p', 'pt', 'a4');
//     var source = document.getElementById(id);
//     var margins = {
//         top: 10,
//         bottom: 10,
//         left: 10
//     };

//     var options = {
//         callback: function (pdf) {
//             pdf.save('Test.pdf');
//         },
//         x: margins.left,
//         y: margins.top,
//         html2canvas: {
//             scale: 0.7 // Adjust the scale factor for better rendering
//         }
//     };

//     doc.html(source, options);
// }

function DownloadSchedule(id) {
    var doc = new jspdf.jsPDF('l', 'pt', 'a4'); // Landscape orientation
    var source = document.getElementById(id);

    // Calculate the center position
    var pageWidth = doc.internal.pageSize.getWidth();
    var sourceWidth = source.offsetWidth;

    var x = (pageWidth - sourceWidth) / 2;
    var y = 10; // You can adjust the vertical position as needed

    var options = {
        callback: function (pdf) {
            pdf.save(id + pdf);
        },
        x: x,
        y: y,
        html2canvas: {
            scale: 0.7, // Adjust the scale factor for better rendering
            backgroundColor: 'white' // Set a background color for better contrast
        },
        pdfCallback: function (pdf) {
            pdf.addPage('l', 'a4'); // Add a new landscape page
            doc.html(source, options);
        }
    };

    doc.html(source, options);
}

// function DownloadSchedule(id) {
//     var doc = new jspdf.jsPDF('l', 'pt', 'a4'); // Landscape orientation
//     var source = document.getElementById(id);

//     // Calculate the width and height of the PDF page
//     var pageWidth = doc.internal.pageSize.getWidth();
//     var pageHeight = doc.internal.pageSize.getHeight();

//     // Calculate the width of the HTML content
//     var sourceWidth = source.offsetWidth;

//     // Calculate the scale factor to fit the content within the page width
//     var scale = pageWidth / sourceWidth;

//     // Align the content to the left border
//     var x = 10; // Adjust this value as needed

//     // Calculate the vertical center position
//     var y = (pageHeight - source.offsetHeight * scale) / 2;

//     var options = {
//         callback: function (pdf) {
//             pdf.save('Test.pdf');
//         },
//         x: x,
//         y: y,
//         html2canvas: {
//             scale: scale,
//             backgroundColor: 'white' // Set a background color for better contrast
//         },
//         pdfCallback: function (pdf) {
//             pdf.addPage('l', 'a4'); // Add a new landscape page
//             doc.html(source, options);
//         }
//     };

//     doc.html(source, options);
// }

