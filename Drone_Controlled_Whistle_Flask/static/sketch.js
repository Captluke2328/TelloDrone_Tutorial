// Copyright (c) 2019 ml5
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

/* ===
ml5 Example
Webcam Image Classification using a pre-trained customized model and p5.js
This example uses p5 preload function to create the classifier
=== */

// Global variable to store the classifier
let classifier;

// Label (start by showing listening)
let label = "listening";

// Teachable Machine model URL:
let soundModelURL = 'https://teachablemachine.withgoogle.com/models/1-OdaTjEM/model.json';
//let soundModelURL = 'http://localhost:8000/Desktop/My_Project/Teachable_Machine_Tutorial/Audio_Classifier/Whistle_UpDownLeftRight_Classifier/model.json';
//let soundModelURL = 'http://127.0.0.1:5000/static/model.json';

let result;
let confidence = 0;

function preload() {
  // Load the mode dl
  classifier = ml5.soundClassifier(soundModelURL);
}

function setup() {
  // createCanvas(640, 240);
  // background(0);

  // Start classifying
  // The sound model will continuously listen to the microphone
  classifier.classify(gotResult);
}

// function draw() {
//   background(0);
//   // Draw the label in the canvas
//   fill(255);
//   textSize(32);
//   textAlign(CENTER, CENTER);
//   text(result, width / 2, height / 2);
// }

// The model recognizing a sound will trigger this event

function gotResult(error, results) {
  if (error) {
    console.error(error);
    return;
  }
  // The results are in an array ordered by confidence.
  // console.log(results[0]);
  label = results[0].label;
  confidence = nf(results[0].confidence, 0, 2)
  // createDiv(`Label: ${results[0].label}`);
  // createDiv(`Confidence: ${nf(results[0].confidence, 0, 2)}`);
  // textSize(25)
  // text(results[0].label,10,height-50)
  
  if (confidence >= 0.90) {
  if (label == 'Left'){
     result = 'Left'
  }

   else if (label == 'Up '){
    result = 'Up'
  }

  else if (label == 'Stop'){
    result = 'Stop'
  }
  else if (label == 'Right') {
    result = 'Right'
  }
  else{
     result = 'Listening'
  }
  
  // createDiv(`Label: ${results[0].label}`);
  // createDiv(`Confidence: ${nf(results[0].confidence, 0, 2)}`);
  // textSize(25)

  //text(results[0].label,10,height-100)
    
  // Draw the label in the canvas
  // background(0);
  // fill(255);
  // textSize(32);
  // textAlign(CENTER, CENTER);
  // text(result, width / 2, height / 2);
  document.getElementById('label').innerHTML = results[0].label
  document.getElementById('result').value = results[0].label
  document.getElementById('myForm').submit();
  }
  
}