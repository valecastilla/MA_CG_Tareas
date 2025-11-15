/*
 * Script to draw a complex shape in 2D
 *
 * Valentina Castilla
 * 2025-11-11
 */

"use strict";

import * as twgl from "twgl-base.js";
import { M3 } from "./A01028209-2d-libs.js";
import GUI from "lil-gui";

// Define the shader code, using GLSL 3.00

const vsGLSL = `#version 300 es
in vec2 a_position;
in vec4 a_color;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

out vec4 v_color;

void main() {
    // Multiply the matrix by the vector, adding 1 to the vector to make
    // it the correct size. Then keep only the two first components
    vec2 position = (u_transforms * vec3(a_position, 1)).xy;

    // Convert the position from pixels to 0.0 - 1.0
    vec2 zeroToOne = position / u_resolution;

    // Convert from 0->1 to 0->2
    vec2 zeroToTwo = zeroToOne * 2.0;

    // Convert from 0->2 to -1->1 (clip space)
    vec2 clipSpace = zeroToTwo - 1.0;

    // Invert Y axis
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);

    // Pass the vertex color to the fragment shader
    v_color = a_color;
}
`;

const fsGLSL = `#version 300 es
precision highp float;

in vec4 v_color;
out vec4 outColor;

void main() {
    outColor = v_color;
}
`;

// Structure for the global data of all objects
// This data will be modified by the UI and used by the renderer
const objects = {
  // Se puede añadir más objetos aquí, model 1, model 2, etc.
  model: {
    // properties of the model
    transforms: {
      t: {
        // translation
        x: 0,
        y: 0,
        z: 0,
      },
      rr: {
        // rotation radians
        x: 0,
        y: 0,
        z: 0,
      },
      s: {
        // scale
        x: 1,
        y: 1,
        z: 1,
      },
    },
    color: [1, 0.84, 0, 1],
  },
  // Pivot only translates
  modelP: {
    // properties of the model
    transforms: {
      t: {
        // translation
        x: 0,
        y: 0,
        z: 0,
      },
    },
    //color: [254 / 255, 128 / 255, 200 / 255, 1],
  },
};

// Initialize the WebGL environmnet
function main() {
  const canvas = document.querySelector("canvas");
  const gl = canvas.getContext("webgl2");
  twgl.resizeCanvasToDisplaySize(gl.canvas);
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

  setupUI(gl);

  const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

  const sides = 20;
  const centerX = 0;
  const centerY = 0;
  const radius = 100;

  const sidesP = 4;
  const centerXP = 0;
  const centerYP = 0;
  const radiusP = 10;

  // Create a polygon with the center at a specific location
  // Face
  //const arraysF = generateData(sides, centerX, centerY, radius);
  // pass GUI color so face uses the current color
  const arraysF = generateDataFace(radius, centerX, centerY, objects.model.color);
  const bufferInfoF = twgl.createBufferInfoFromArrays(gl, arraysF);
  const vaoF = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfoF);

  // Pivot
  const arraysP = generateData(sidesP, centerXP, centerYP, radiusP);
  const bufferInfoP = twgl.createBufferInfoFromArrays(gl, arraysP);
  const vaoP = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfoP);

  // Draw face
  drawScene(gl, vaoF, programInfo, bufferInfoF, vaoP, bufferInfoP);
  //drawScene(gl, vaoF, programInfo, bufferInfoF);

}

// Function to do the actual display of the objects
function drawScene(gl, vao, programInfo, bufferInfo, vaoP, bufferInfoP) {
  // Clear canvas
  gl.clearColor(0, 0, 0, 0);
  gl.clear(gl.COLOR_BUFFER_BIT); // Clears canvas so that both objects can be redrawn

  // --- Face ---
  let translate = [objects.model.transforms.t.x, objects.model.transforms.t.y];
  let angle_radians = objects.model.transforms.rr.z;
  let scale = [objects.model.transforms.s.x, objects.model.transforms.s.y];

  // --- Pivot ---
  let translateP = [
    objects.modelP.transforms.t.x,
    objects.modelP.transforms.t.y,
  ];

  // Create transform matrices
  const scaMat = M3.scale(scale);
  const rotMat = M3.rotation(angle_radians);
  const traMat = M3.translation(translate);

  
  const traMatP = M3.translation(translateP);

  // Composite for face (rotate around pivot)
  // Pivot base coordinates used when the geometry was created in main()
  const pivotBase = [0, 0]; // same centerXP, centerYP used in main()
  const pivotCurrentPos = [
    pivotBase[0] + objects.modelP.transforms.t.x,
    pivotBase[1] + objects.modelP.transforms.t.y,
  ];

  // Translate to pivot, rotate, translate back (then apply face translation)
  const toPivot = M3.translation([-pivotCurrentPos[0], -pivotCurrentPos[1]]);
  const backFromPivot = M3.translation([pivotCurrentPos[0], pivotCurrentPos[1]]);

  let transforms = M3.identity();
  // For rotation move object to pivot, rotate, move back
  transforms = M3.multiply(traMat, transforms); 
  transforms = M3.multiply(scaMat, transforms); 
  transforms = M3.multiply(toPivot, transforms);
  transforms = M3.multiply(rotMat, transforms);
  transforms = M3.multiply(backFromPivot, transforms); 

  let uniforms = {
    u_resolution: [gl.canvas.width, gl.canvas.height],
    u_transforms: transforms,
  };

  // Composite for pivot
  let transformsP = M3.identity();
  transformsP = M3.multiply(traMatP, transformsP);

  let uniformsP = {
    u_resolution: [gl.canvas.width, gl.canvas.height],
    u_transforms: transformsP,
  };

  gl.useProgram(programInfo.program);

  // Draw face
  twgl.setUniforms(programInfo, uniforms);
  gl.bindVertexArray(vao);
  twgl.drawBufferInfo(gl, bufferInfo);

  // Draw pivot
  twgl.setUniforms(programInfo, uniformsP);
  gl.bindVertexArray(vaoP);
  twgl.drawBufferInfo(gl, bufferInfoP);

  requestAnimationFrame(() => drawScene(gl, vao, programInfo, bufferInfo, vaoP, bufferInfoP));
}

function setupUI(gl) {
  // Crea interfaz que permite modificar los objetos
  const gui = new GUI(); // Crear estancia clase UI

  const traFolder = gui.addFolder("Translation"); // Carpeta para agrupar controles de traslación
  traFolder.add(objects.model.transforms.t, "x", 0, gl.canvas.width); // Rango en el que se puede mover el objeto
  traFolder.add(objects.model.transforms.t, "y", 0, gl.canvas.height);

  const rotFolder = gui.addFolder("Rotation"); // Carpeta para agrupar controles de rotación
  rotFolder.add(objects.model.transforms.rr, "z", 0, Math.PI * 2);

  const scaFolder = gui.addFolder("Scale"); // Carpeta para agrupar controles de escala
  scaFolder.add(objects.model.transforms.s, "x", -5, 5);
  scaFolder.add(objects.model.transforms.s, "y", -5, 5);

  const traFolderP = gui.addFolder("Translation Pivot"); // Carpeta para agrupar controles de traslación
  traFolderP.add(objects.modelP.transforms.t, "x", 0, gl.canvas.width); // Rango en el que se puede mover el objeto
  traFolderP.add(objects.modelP.transforms.t, "y", 0, gl.canvas.height);
}

// Create the data for the vertices of the polyton, as an object with two arrays
function generateData(sides, centerX, centerY, radius) {
    // The arrays are initially empty
    let arrays =
    {
        // Two components for each position in 2D
        a_position: { numComponents: 2, data: [] },
        // Four components for a color (RGBA)
        a_color:    { numComponents: 4, data: [] },
        // Three components for each triangle, the 3 vertices
        indices:  { numComponents: 3, data: [] }
    };

    // Initialize the center vertex, at the origin and with white color
    arrays.a_position.data.push(centerX); // empezar donde se dijo
    arrays.a_position.data.push(centerY);
    arrays.a_color.data.push(1);
    arrays.a_color.data.push(1);
    arrays.a_color.data.push(1);
    arrays.a_color.data.push(1);

    let angleStep = 2 * Math.PI / sides;
    // Loop over the sides to create the rest of the vertices
    for (let s=0; s<sides; s++) {
        let angle = angleStep * s;
        // Generate the coordinates of the vertex
        let x = centerX + Math.cos(angle) * radius;
        let y = centerY + Math.sin(angle) * radius;
        arrays.a_position.data.push(x);
        arrays.a_position.data.push(y);
        // Generate a random color for the vertex
        arrays.a_color.data.push(Math.random());
        arrays.a_color.data.push(Math.random());
        arrays.a_color.data.push(Math.random());
        arrays.a_color.data.push(1);
        // Define the triangles, in counter clockwise order
        arrays.indices.data.push(0);
        arrays.indices.data.push(s + 1);
        arrays.indices.data.push(((s + 2) <= sides) ? (s + 2) : 1);
    }
    console.log(arrays);

    return arrays;
}

function generateDataFace(r, centerX = 0, centerY = 0, color = [1, 0.84, 0, 1]) {
  // Create base face polygon
  const sides = 20;
  const arrays = generateData(sides, centerX, centerY, r);

  const numVerts = arrays.a_position.data.length / 2;
  arrays.a_color.data = [];
  for (let i = 0; i < numVerts; i++) {
    arrays.a_color.data.push(...color);
  }

  // Function to add a triangle to arrays
  const addTriangle = (x1, y1, x2, y2, x3, y3, color = [0, 0, 0, 1]) => {
    arrays.a_position.data.push(x1, y1, x2, y2, x3, y3); // three new vertices
    arrays.a_color.data.push(...color, ...color, ...color); // colors for the three vertices
    const base = arrays.a_position.data.length / 2 - 3; // index of first new vertex
    arrays.indices.data.push(base, base + 1, base + 2); // create triangle
  };

  // Eyes
  const eyeOffsetX = r / 3;
  const eyeOffsetY = r / 4;
  const eyeSize = r / 10;
  const leftX = centerX - eyeOffsetX;
  const leftY = centerY - eyeOffsetY;
  const rightX = centerX + eyeOffsetX;
  const rightY = centerY - eyeOffsetY;

  addTriangle(leftX - eyeSize, leftY + eyeSize, leftX + eyeSize, leftY + eyeSize, leftX, leftY - eyeSize);
  addTriangle(rightX - eyeSize, rightY + eyeSize, rightX + eyeSize, rightY + eyeSize, rightX, rightY - eyeSize);

  // Mouth
  const mouthOffsetY = r * 0.35;
  const mouthWidth = r * 1;
  const mouthHeight = r * 0.20;
  const mouthLeftX = centerX - mouthWidth / 2;
  const mouthRightX = centerX + mouthWidth / 2;
  const mouthY = centerY + mouthOffsetY;
  const mouthTipY = mouthY + mouthHeight;

  addTriangle(mouthLeftX, mouthY, mouthRightX, mouthY, centerX, mouthTipY);

  return arrays;
}


main();

