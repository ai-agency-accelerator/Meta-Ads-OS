// Entrada del bundle vendorizado de three.js (r181.2) + addons que usa cutkit/motion/three/ck3d.js.
// Se compila a three.ck.min.js (IIFE, sin CDN) con build.sh. NO editar el .min.js a mano.
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { Pass, FullScreenQuad } from "three/addons/postprocessing/Pass.js";
import { CopyShader } from "three/addons/shaders/CopyShader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { SVGLoader } from "three/addons/loaders/SVGLoader.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RectAreaLightUniformsLib } from "three/addons/lights/RectAreaLightUniformsLib.js";
import * as BufferGeometryUtils from "three/addons/utils/BufferGeometryUtils.js";

window.THREE = THREE;
window.THREE_ADDONS = {
  EffectComposer, RenderPass, ShaderPass, UnrealBloomPass, OutputPass, Pass, FullScreenQuad, CopyShader,
  RoomEnvironment, SVGLoader, RoundedBoxGeometry, RectAreaLightUniformsLib, BufferGeometryUtils,
};
