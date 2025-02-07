console.log("Testing alooo...");
// // Get the modal content element
// var modalContent = document.getElementById('screen_body');
// var screenshotButton = document.getElementById('screen');

// function takeScreenshot() {
//     // Create a canvas element and draw the modal content on it
//     var canvas = document.createElement('canvas');
//     canvas.width = modalContent.offsetWidth;
//     canvas.height = modalContent.offsetHeight;
//     var ctx = canvas.getContext('2d');

//     // Create an image of the modal content
//     var modalImage = new Image();
    
//     // Use a data URI representing the content of the modal
//     modalImage.src = 'data:image/svg+xml;base64,' + btoa('<svg xmlns="http://www.w3.org/2000/svg" width="' + modalContent.offsetWidth + '" height="' + modalContent.offsetHeight + '">' +
//         '<foreignObject width="100%" height="100%">' +
//         new XMLSerializer().serializeToString(modalContent) +
//         '</foreignObject>' +
//         '</svg>');

//     // Once the image has loaded, draw it onto the canvas
//     modalImage.onload = function () {
//         ctx.drawImage(modalImage, 0, 0, modalContent.offsetWidth, modalContent.offsetHeight);

//         // Convert the canvas content to a data URL
//         var dataURL = canvas.toDataURL('image/png');

//         // Create a download link and trigger the download
//         var downloadLink = document.createElement('a');
//         downloadLink.href = dataURL;
//         downloadLink.download = 'modal_screenshot.png';
//         document.body.appendChild(downloadLink);
//         downloadLink.click();
//         document.body.removeChild(downloadLink);
//     };
// }

// screenshotButton.addEventListener('click', takeScreenshot);


// const screen = document.getElementById('screen').addEventListener('click', function () {
//     html2canvas($("#screen_body"), {
//     useCORS: true,
//     onrendered: function(canvas) {
//         canvas = canvas;
//         canvas.toBlob(function(blob) {
//             saveAs(blob, "Project.png");
//             });
//         }
//     });
// });


document.getElementById('screen').addEventListener('click', function () {
    // console.log("pass");
    html2canvas(document.getElementById('screen_body'), {
        backgroundColor: 'transparent' // Set the background color to transparent
    }).then(function (canvas) {
        // Convert the canvas to a data URL
        var imgData = canvas.toDataURL('image/png');
        console.log("Hello JS");
        // Create a link element to download the image
        var a = document.createElement('a');
        a.href = imgData;
        a.download = 'screenshot.png';
        a.click();
    });
});
