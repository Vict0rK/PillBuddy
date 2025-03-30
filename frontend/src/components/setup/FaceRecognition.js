// import React, { useRef, useState } from "react";

// const FaceRecognition = ({ existingImage, onCapture }) => {
//   const videoRef = useRef(null);
//   const [cameraOn, setCameraOn] = useState(false);
//   // Initialize capturedImage from existingImage if provided
//   const [capturedImage, setCapturedImage] = useState(existingImage || null);

//   const startCamera = () => {
//     navigator.mediaDevices
//       .getUserMedia({ video: true })
//       .then((stream) => {
//         if (videoRef.current) {
//           videoRef.current.srcObject = stream;
//           setCameraOn(true);
//         }
//       })
//       .catch((err) => {
//         console.error("Error accessing webcam:", err);
//         setCameraOn(false);
//       });
//   };

//   const captureImage = () => {
//     if (!cameraOn || !videoRef.current) return;
//     const canvas = document.createElement("canvas");
//     canvas.width = videoRef.current.videoWidth;
//     canvas.height = videoRef.current.videoHeight;
//     const ctx = canvas.getContext("2d");
//     ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

//     const imageData = canvas.toDataURL("image/png");
//     setCapturedImage(imageData);

//     if (onCapture) onCapture(imageData);

//     // Stop the camera
//     if (videoRef.current.srcObject) {
//       videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
//     }
//   };

//   const retakeImage = () => {
//     setCapturedImage(null);
//     setCameraOn(false);
//   };

//   return (
//     <div className="flex flex-col items-center">
//       {capturedImage ? (
//         // If there's already a captured image, display it
//         <div className="flex flex-col items-center">
//           <img src={capturedImage} alt="Captured Face" className="border rounded" />
//           <button
//             onClick={retakeImage}
//             className="mt-4 bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition-all"
//           >
//             Retake
//           </button>
//         </div>
//       ) : (
//         // Otherwise, show video preview (if started) or allow the user to start camera
//         <div className="flex flex-col items-center">
//           <video ref={videoRef} autoPlay className="border m-6" />
//           <div className="flex justify-center mt-2 space-x-2">
//             <button
//               onClick={startCamera}
//               className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
//             >
//               Start Camera
//             </button>
//             <button
//               onClick={captureImage}
//               disabled={!cameraOn}
//               className={`bg-green-500 text-white p-2 rounded transition-all ${
//                 cameraOn ? "hover:bg-green-600" : "opacity-50 cursor-not-allowed"
//               }`}
//             >
//               Capture
//             </button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default FaceRecognition;

import React, { useState } from "react";

const FaceRecognition = ({ existingImage, onCapture }) => {
  const [uploadedImage, setUploadedImage] = useState(existingImage || null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target.result);
        if (onCapture) onCapture(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setUploadedImage(null);
  };

  return (
    <div className="flex flex-col items-center">
      {uploadedImage ? (
        <div className="flex flex-col items-center">
          <img src={uploadedImage} alt="Uploaded Face" className="border rounded" />
          <button
            onClick={removeImage}
            className="mt-4 bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition-all"
          >
            Remove
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <label className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 cursor-pointer">
            Upload Image
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleImageUpload}
            />
          </label>
        </div>
      )}
    </div>
  );
};

export default FaceRecognition;
