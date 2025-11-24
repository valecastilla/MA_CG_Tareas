/*
 * Scene to display an OBJ loaded model using Object3D and loadObj
 *
 * Based on 01_cube.js
 */

'use strict';

import * as twgl from 'twgl-base.js';
import GUI from 'lil-gui';
import { M4 } from './3d-lib';
import { Object3D } from './object3d';

// Shaders
import vsGLSL from '../assets/shaders/vs_color.glsl?raw';
import fsGLSL from '../assets/shaders/fs_color.glsl?raw';

// OBJ data example taken from obj_loader.js
// It defines a cube with vertex positions and normals
const objText = `
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0
v -1.0 -1.0 -1.0
v -1.0  1.0 -1.0
v  1.0  1.0 -1.0
v  1.0 -1.0 -1.0
v -1.0  1.0 -1.0
v -1.0  1.0  1.0
v  1.0  1.0  1.0
v  1.0  1.0 -1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0 -1.0  1.0
v -1.0 -1.0  1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v  1.0  1.0  1.0
v  1.0 -1.0  1.0
v -1.0 -1.0 -1.0
v -1.0 -1.0  1.0
v -1.0  1.0  1.0
v -1.0  1.0 -1.0
vn  0.0  0.0  1.0
vn  0.0  0.0 -1.0
vn  0.0  1.0  0.0
vn  0.0 -1.0  0.0
vn  1.0  0.0  0.0
vn -1.0  0.0  0.0
f  1//1  2//1  3//1
f  1//1  3//1  4//1
f  5//2  6//2  7//2
f  5//2  7//2  8//2
f  9//3 10//3 11//3
f  9//3 11//3 12//3
f 13//4 14//4 15//4
f 13//4 15//4 16//4
f 17//5 18//5 19//5
f 17//5 19//5 20//5
f 21//6 22//6 23//6
f 21//6 23//6 24//6`;

// Global variables
let programInfo = undefined;
let gl = undefined;

// Array of objects to render
const objects = [];

function main() {
    // Setup the canvas and WebGL2
    const canvas = document.querySelector('canvas');
    gl = canvas.getContext('webgl2');
    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    // Prepare the program with the shaders
    programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    // Prepare the object to be drawn
    // Now we pass objText to prepareVAO so it uses loadObj instead of cubeFaceColors
    const objModel = new Object3D(1);
    objModel.prepareVAO(gl, programInfo, objText);
    objects.push(objModel);

    // Prepare the user interface
    setupUI(objModel);

    drawScene();
}

function drawObject(gl, programInfo, object, viewProjectionMatrix) {
    // Translation and scale vectors
    const v3_tra = [object.position.x,
                    object.position.y,
                    object.position.z];
    const v3_sca = [object.scale.x,
                    object.scale.y,
                    object.scale.z];

    // Individual transform matrices
    const scaMat = M4.scale(v3_sca);
    const rotXMat = M4.rotationX(object.rotRad.x);
    const rotYMat = M4.rotationY(object.rotRad.y);
    const rotZMat = M4.rotationZ(object.rotRad.z);
    const traMat = M4.translation(v3_tra);

    // Composite transform
    let transforms = M4.identity();
    transforms = M4.multiply(scaMat, transforms);
    transforms = M4.multiply(rotXMat, transforms);
    transforms = M4.multiply(rotYMat, transforms);
    transforms = M4.multiply(rotZMat, transforms);
    transforms = M4.multiply(traMat, transforms);

    object.matrix = transforms;

    // World View Projection
    const wvpMat = M4.multiply(viewProjectionMatrix, transforms);

    const uniforms = {
        u_transforms: wvpMat,
    };

    twgl.setUniforms(programInfo, uniforms);
    gl.bindVertexArray(object.vao);
    twgl.drawBufferInfo(gl, object.bufferInfo);
}

function drawScene() {
    // Clear the canvas
    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    // Enable back face culling
    gl.enable(gl.CULL_FACE);

    gl.useProgram(programInfo.program);

    const viewProjectionMatrix = setupViewProjection(gl);

    // Draw the only object in the scene
    drawObject(gl, programInfo, objects[0], viewProjectionMatrix);

    requestAnimationFrame(() => drawScene(gl));
}

function setupViewProjection(gl) {
    const fov = 60 * Math.PI / 180;
    const aspect = gl.canvas.clientWidth / gl.canvas.clientHeight;

    const projectionMatrix = M4.perspective(fov, aspect, 1, 200);

    const cameraPosition = [0, 0, 10];
    const target = [0, 0, 0];
    const up = [0, 1, 0];

    const cameraMatrix = M4.lookAt(cameraPosition, target, up);
    const viewMatrix = M4.inverse(cameraMatrix);
    const viewProjectionMatrix = M4.multiply(projectionMatrix, viewMatrix);

    return viewProjectionMatrix;
}

function setupUI(object) {
    const gui = new GUI();

    const traFolder = gui.addFolder('Translation:');
    traFolder.add(object.position, 'x', -5, 5);
    traFolder.add(object.position, 'y', -5, 5);
    traFolder.add(object.position, 'z', -5, 5);

    const rotFolder = gui.addFolder('Rotation:');
    rotFolder.add(object.rotDeg, 'x', -360, 360)
        .decimals(2)
        .onChange(value => {
            object.rotRad.x = value * Math.PI / 180.0;
        });
    rotFolder.add(object.rotDeg, 'y', -360, 360)
        .decimals(2)
        .onChange(value => {
            object.rotRad.y = value * Math.PI / 180.0;
        });
    rotFolder.add(object.rotDeg, 'z', -360, 360)
        .decimals(2)
        .onChange(value => {
            object.rotRad.z = value * Math.PI / 180.0;
        });

    const scaFolder = gui.addFolder('Scale:');
    scaFolder.add(object.scale, 'x', -5, 5);
    scaFolder.add(object.scale, 'y', -5, 5);
    scaFolder.add(object.scale, 'z', -5, 5);
}

main();