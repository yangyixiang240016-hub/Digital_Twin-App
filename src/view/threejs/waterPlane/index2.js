import * as THREE from 'three';
import {
    Color,
    Matrix4,
    Mesh,
    PerspectiveCamera,
    Plane,
    ShaderMaterial,
    UniformsLib,
    UniformsUtils,
    Vector3,
    Vector4,
    WebGLRenderTarget
} from 'three';

// 水池名称数组，通过名称在污水厂模型中找到对应模型
const waterPoolNameArr = [
    '初沉池水面1',
    '初沉池水面1001',
    '南北生物池水面',
    '东西生物池-东水面1',
    '东西生物池-东水面2',
    '东西生物池-西水面1',
    '东西生物池-西水面2',
    '二沉池3水面',
    '二沉池3水面001',
    '二沉池4水面',
    '二沉池4水面001',
    '高效沉淀池水面',
    'v滤池水',
];

// 最开始的水面，渲染更新这个一个水面，其余的水面也会跟着生效，以此减少性能消耗
let startWaterPlane;
const waterGeometryArr = [];
// 创建一个水面组对象，存储所有水面
const waterPlaneGroup = new THREE.Group();
waterPlaneGroup.rotateY(Math.PI / 2);
// 加载纹理贴图
const texture = new THREE.TextureLoader().load(
    "./waternormals.jpg",
    function (texture) {
        texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    }
)
const uFrequency = 0.0;
const textureWidth = 256;
const textureHeight = 256;
const clipBias = 0.0;
const alpha = 1.0;
const time = 0.0;
const normalSampler = texture;
const sunDirection = new THREE.Vector3(0.70707, 0.70707, 0);
const sunColor = new THREE.Color('#fff');
const waterColor = new THREE.Color('#879d73');
const eye = new Vector3(0, 0, 0);
const distortionScale = 1;
const side = THREE.FrontSide;
const fog = false;
const mirrorPlane = new Plane();
const normal = new Vector3();
const mirrorWorldPosition = new Vector3();
const cameraWorldPosition = new Vector3();
const rotationMatrix = new Matrix4();
let lookAtPosition = new Vector3(0, 0, 0);
const clipPlane = new Vector4();
const view = new Vector3();
const target = new Vector3();
const q = new Vector4();
const textureMatrix = new Matrix4();
const mirrorCamera = new PerspectiveCamera();
const renderTarget = new WebGLRenderTarget(textureWidth, textureHeight);
const mirrorShader = {
    uniforms: UniformsUtils.merge([
        UniformsLib['fog'],
        UniformsLib['lights'],
        {
            'normalSampler': { value: null },
            'mirrorSampler': { value: null },
            'alpha': { value: 1.0 },
            'time': { value: 0.0 },
            'size': { value: 1.0 },
            'distortionScale': { value: 20.0 },
            'textureMatrix': { value: new Matrix4() },
            'sunColor': { value: new Color(0x000000) },
            'sunDirection': { value: new Vector3(0, 0, 0) },
            'eye': { value: new Vector3() },
            'waterColor': { value: waterColor },
            'uFrequency': new THREE.Vector2(50, 100),
        }
    ]),
    vertexShader: /* glsl */`
		// 频率
		uniform vec2 uFrequency;
        uniform mat4 textureMatrix;
        uniform float time;
        varying vec4 mirrorCoord;
        varying vec4 worldPosition;
        #include <common>
        #include <fog_pars_vertex>
        #include <shadowmap_pars_vertex>
        #include <logdepthbuf_pars_vertex>
        void main() {
            mirrorCoord = modelMatrix * vec4( position, 1.0 );
            worldPosition = mirrorCoord.xyzw;
            mirrorCoord = textureMatrix * mirrorCoord;

            vec4 mvPosition = modelMatrix * vec4(position, 1.0);

            // 基础波浪
            float wave1 = sin(mvPosition.x * uFrequency.x + time) * 0.05;
            float wave2 = sin(mvPosition.z * uFrequency.y + time) * 0.05;

            // 增加第二组波浪，频率和振幅不同，增加复杂度
            float wave3 = sin(mvPosition.x * uFrequency.x * 0.5 - time * 1.5) * 0.025;
            float wave4 = sin(mvPosition.z * uFrequency.y * 0.5 - time * 1.5) * 0.025;

            // 合成波浪效果
            mvPosition.y += wave1 + wave2 + wave3 + wave4;

            // 应用视图变换和投影变换
            mvPosition = viewMatrix * mvPosition;
            gl_Position = projectionMatrix * mvPosition;

            #include <beginnormal_vertex>
            #include <defaultnormal_vertex>
            #include <logdepthbuf_vertex>
            #include <fog_vertex>
            #include <shadowmap_vertex>
        }`,
    fragmentShader: /* glsl */`
				uniform sampler2D mirrorSampler;
				uniform float alpha;
				uniform float time;
				uniform float size;
				uniform float distortionScale;
				uniform sampler2D normalSampler;
				uniform vec3 sunColor;
				uniform vec3 sunDirection;
				uniform vec3 eye;
				uniform vec3 waterColor;
				varying vec4 mirrorCoord;
				varying vec4 worldPosition;

                // 获取噪波纹理
				vec4 getNoise( vec2 uv ) {
					vec2 uv0 = ( uv / 103.0 ) + vec2(time / 17.0, time / 29.0);
					vec2 uv1 = uv / 107.0-vec2( time / -19.0, time / 31.0 );
					vec2 uv2 = uv / vec2( 8907.0, 9803.0 ) + vec2( time / 101.0, time / 97.0 );
					vec2 uv3 = uv / vec2( 1091.0, 1027.0 ) - vec2( time / 109.0, time / -113.0 );
					vec4 noise = texture2D( normalSampler, uv0 ) +
						texture2D( normalSampler, uv1 ) +
						texture2D( normalSampler, uv2 ) +
						texture2D( normalSampler, uv3 );
					return noise * 0.5 - 1.0;
				}
                // 获取太阳光
				void sunLight( const vec3 surfaceNormal, const vec3 eyeDirection, float shiny, float spec, float diffuse, inout vec3 diffuseColor, inout vec3 specularColor ) {
                    // 反射
					vec3 reflection = normalize( reflect( -sunDirection, surfaceNormal ) );
                    // 方向
					float direction = max( 0.0, dot( eyeDirection, reflection ) );
					specularColor += pow( direction, shiny ) * sunColor * spec;
					diffuseColor += max( dot( sunDirection, surfaceNormal ), 0.0 ) * sunColor * diffuse;
				}

				#include <common>
				#include <packing>
				#include <bsdfs>
				#include <fog_pars_fragment>
				#include <logdepthbuf_pars_fragment>
				#include <lights_pars_begin>
				#include <shadowmap_pars_fragment>
				#include <shadowmask_pars_fragment>

				void main() {

					#include <logdepthbuf_fragment>
					vec4 noise = getNoise( worldPosition.xz * size );
                    // 表面法线
					vec3 surfaceNormal = normalize( noise.xzy * vec3( 1.5, 1.0, 1.5 ) );
                    // 散射光 
					vec3 diffuseLight = vec3(0.0);
                    // 镜面光
					vec3 specularLight = vec3(0.0);
                    vec3 eyes = vec3(-134.76849917145864,12.563661737564908,104.51194486087573);

					vec3 worldToEye = eyes-worldPosition.xyz;
					vec3 eyeDirection = normalize( worldToEye );
					sunLight( surfaceNormal, eyeDirection, 10.0, 0.1, 0.5, diffuseLight, specularLight );

					float distance = length(worldToEye);

					vec2 distortion = surfaceNormal.xz * ( 0.001 + 1.0 / distance ) * distortionScale;
					vec3 reflectionSample = vec3( texture2D( mirrorSampler, mirrorCoord.xy / mirrorCoord.w + distortion ) );

					float theta = max( dot( eyeDirection, surfaceNormal ), 0.0 );
					float rf0 = 0.1;
					float reflectance = rf0 + ( 1.0 - rf0 ) * pow( ( 1.0 - theta ), 5.0 );
					vec3 scatter = max( 0.0, dot( surfaceNormal, eyeDirection ) ) * waterColor;
                    // * getShadowMask()
					vec3 albedo = mix( ( sunColor * diffuseLight * 0.3 + scatter ) * getShadowMask(), ( waterColor + reflectionSample * 0.3 + reflectionSample * specularLight ), reflectance);
					vec3 outgoingLight = albedo;
					gl_FragColor = vec4( outgoingLight, alpha );

					#include <tonemapping_fragment>
					#include <fog_fragment>
				}`
};

// 水面对象渲染前所执行
function onBeforeRenders (renderer, scene, camera) {
    // 设置水面世界位置
    mirrorWorldPosition.setFromMatrixPosition(startWaterPlane.matrixWorld);
    // 设置相机世界位置
    cameraWorldPosition.setFromMatrixPosition(camera.matrixWorld);
    // 获取世界矩阵中的旋转分量
    rotationMatrix.extractRotation(startWaterPlane.matrixWorld);
    // 设置法线
    normal.set(0, 0, 1);
    // 乘以旋转矩阵
    normal.applyMatrix4(rotationMatrix);
    // 设置view为水面世界位置减去相机世界位置
    view.subVectors(mirrorWorldPosition, cameraWorldPosition);
    // Avoid rendering when mirror is facing away
    // 水面不在相机视角内时则不继续渲染
    // if (view.dot(normal) > 0) return;
    view.reflect(normal).negate();
    // 与水面世界位置相加
    view.add(mirrorWorldPosition);
    // 获取相机矩阵中的旋转分量
    rotationMatrix.extractRotation(camera.matrixWorld);

    // 观察点位置
    lookAtPosition.set(0, 0, -1);
    // 乘以旋转矩阵
    lookAtPosition.applyMatrix4(rotationMatrix);
    // 与相机世界位置相加
    lookAtPosition.add(cameraWorldPosition);

    target.subVectors(mirrorWorldPosition, lookAtPosition);
    target.reflect(normal).negate();
    target.add(mirrorWorldPosition);
    mirrorCamera.position.copy(view);
    mirrorCamera.up.set(0, 1, 0);
    mirrorCamera.up.applyMatrix4(rotationMatrix);
    mirrorCamera.up.reflect(normal);
    mirrorCamera.lookAt(target);

    mirrorCamera.far = camera.far; // Used in WebGLBackground
    mirrorCamera.updateMatrixWorld();
    mirrorCamera.projectionMatrix.copy(camera.projectionMatrix);

    // Update the texture matrix
    textureMatrix.set(
        0.5, 0.0, 0.0, 0.5,
        0.0, 0.5, 0.0, 0.5,
        0.0, 0.0, 0.5, 0.5,
        0.0, 0.0, 0.0, 1.0
    );
    textureMatrix.multiply(mirrorCamera.projectionMatrix);
    textureMatrix.multiply(mirrorCamera.matrixWorldInverse);

    // Now update projection matrix with new clip plane, implementing code from: http://www.terathon.com/code/oblique.html
    // Paper explaining this technique: http://www.terathon.com/lengyel/Lengyel-Oblique.pdf
    mirrorPlane.setFromNormalAndCoplanarPoint(normal, mirrorWorldPosition);
    mirrorPlane.applyMatrix4(mirrorCamera.matrixWorldInverse);
    clipPlane.set(mirrorPlane.normal.x, mirrorPlane.normal.y, mirrorPlane.normal.z, mirrorPlane.constant);
    // const projectionMatrix = mirrorCamera.projectionMatrix;
    // q.x = (Math.sign(clipPlane.x) + projectionMatrix.elements[8]) / projectionMatrix.elements[0];
    // q.y = (Math.sign(clipPlane.y) + projectionMatrix.elements[9]) / projectionMatrix.elements[5];
    // q.z = - 1.0;
    // q.w = (1.0 + projectionMatrix.elements[10]) / projectionMatrix.elements[14];
    // // Calculate the scaled plane vector
    // clipPlane.multiplyScalar(2.0 / clipPlane.dot(q));
    // // Replacing the third row of the projection matrix
    // projectionMatrix.elements[2] = clipPlane.x;
    // projectionMatrix.elements[6] = clipPlane.y;
    // projectionMatrix.elements[10] = clipPlane.z + 1.0 - clipBias;
    // projectionMatrix.elements[14] = clipPlane.w;
    // const m = new THREE.Matrix4();
    // m.set(0.3907683860941631,
    //     2.7755575615628914e-17,
    //     -0.9204890376475775,
    //     0,
    //     -0.19750628641114223,
    //     0.9767093402572705,
    //     -0.08384587933993708,
    //     0,
    //     0.8990502406748152,
    //     0.21456669045825222,
    //     0.3816671325754284,
    //     0,
    //     194.8014089303765,
    //     48.09116558761228,
    //     82.69759775861318,
    //     1);
    // eye.setFromMatrixPosition(m);

    // eye.setFromMatrixPosition(camera.matrixWorld);
    // Render
    const currentRenderTarget = renderer.getRenderTarget();
    const currentXrEnabled = renderer.xr.enabled;
    const currentShadowAutoUpdate = renderer.shadowMap.autoUpdate;
    startWaterPlane.visible = false;
    renderer.xr.enabled = false; // Avoid camera modification and recursion
    renderer.shadowMap.autoUpdate = false; // Avoid re-computing shadows
    renderer.setRenderTarget(renderTarget);
    renderer.state.buffers.depth.setMask(true); // make sure the depth buffer is writable so it can be properly cleared, see #18897
    if (renderer.autoClear === false) renderer.clear();
    renderer.render(scene, mirrorCamera);
    startWaterPlane.visible = true;
    // renderer.xr.enabled = currentXrEnabled;
    // renderer.shadowMap.autoUpdate = currentShadowAutoUpdate;
    renderer.setRenderTarget(currentRenderTarget);
    // Restore viewport
    const viewport = camera.viewport;
    if (viewport !== undefined) {
        renderer.state.viewport(viewport);
    }
};

// 创建水面
function createWaterPlane (model, envMap) {
    model.add(waterPlaneGroup);
    // 创建水面
    waterPoolNameArr.map((name, index) => {
        const planeObj = model.getObjectByName(name);
        planeObj.visible = false;
        // 南北生物池尺寸需要兼容处理一下
        if (name === '南北生物池水面') {
            // 获取水面模型尺寸
            const box = planeObj.geometry.boundingBox;
            // 计算出水面模型的长度和宽度
            const x = box.max.x - box.min.x;
            const z = box.max.z - box.min.z;
            const geometry = new THREE.PlaneGeometry(z, x - 1.2, 200, 200);
            const position = planeObj.getWorldPosition(new THREE.Vector3());
            position.y += 0.2;
            position.z += -0.2;
            waterGeometryArr.push({
                geometry: geometry,
                position: position,
                name: name
            })
        }
        // 初沉池和二沉池为圆形建筑，需要使用圆形平面
        else if (name.indexOf('沉池') !== -1) {
            planeObj.visible = false;
            // 获取水面模型尺寸
            const box = planeObj.geometry.boundingBox;
            // 计算出水面模型的半径
            let radius = (box.max.x - box.min.x) / 2;
            if (name.indexOf('二') !== -1) {
                radius += 3;
            }
            const geometry = new THREE.CircleGeometry(radius, 128);
            const position = planeObj.getWorldPosition(new THREE.Vector3());
            position.y -= 0.1;
            waterGeometryArr.push({
                geometry: geometry,
                position: position,
                name: name
            })
        } else {
            // 获取水面模型尺寸
            const box = planeObj.geometry.boundingBox;
            // 计算出水面模型的长度和宽度
            const x = box.max.x - box.min.x;
            const z = box.max.z - box.min.z;
            const geometry = new THREE.PlaneGeometry(z, x, 200, 200);
            const position = planeObj.getWorldPosition(new THREE.Vector3());
            if (name.indexOf('沉淀池') !== -1) position.y += 0.3;
            else if (name.indexOf('滤池') !== -1) position.y += 0.1;
            else position.y -= 0.05;
            waterGeometryArr.push({
                geometry: geometry,
                position: position,
                name: name
            })
        }
    })
    // 水面材质
    const material = new ShaderMaterial({
        fragmentShader: mirrorShader.fragmentShader,
        vertexShader: mirrorShader.vertexShader,
        uniforms: UniformsUtils.clone(mirrorShader.uniforms),
        lights: true,
        side: side,
        fog: fog,
        depthWrite: false,
        transparent: true,
        lights: true,
    });
    // 水面采样器
    material.uniforms['mirrorSampler'].value = renderTarget.texture;
    // 纹理矩阵
    material.uniforms['textureMatrix'].value = textureMatrix;
    material.uniforms['alpha'].value = alpha;
    material.uniforms['time'].value = time;
    // 法线采样器
    material.uniforms['normalSampler'].value = normalSampler;
    // 太阳颜色
    material.uniforms['sunColor'].value = sunColor;
    // 太阳方向
    material.uniforms['sunDirection'].value = sunDirection;
    material.uniforms['distortionScale'].value = distortionScale;
    material.uniforms['eye'].value = eye;
    material.uniforms['uFrequency'].value = new THREE.Vector2(5, 10);
    // 最开始的水面，渲染更新这个一个水面，其余的水面也会跟着生效，以此减少性能消耗
    startWaterPlane = new Mesh(waterGeometryArr[0].geometry, material);
    startWaterPlane.rotateX(-Math.PI / 2);
    startWaterPlane.position.copy(waterGeometryArr[0].position);
    startWaterPlane.renderOrder = 100;
    startWaterPlane.name = waterGeometryArr[0].name;
    startWaterPlane.color = new THREE.Color('#879d73');
    // 渲染前执行更新
    startWaterPlane.onBeforeRender = onBeforeRenders;
    waterPlaneGroup.add(startWaterPlane);
    waterGeometryArr.map((obj, index) => {
        // 避开已经创建过的的第一个水面
        if (index) {
            // 水面材质
            const material = new ShaderMaterial({
                fragmentShader: mirrorShader.fragmentShader,
                vertexShader: mirrorShader.vertexShader,
                uniforms: UniformsUtils.clone(mirrorShader.uniforms),
                lights: true,
                side: side,
                fog: fog,
                depthWrite: false,
                transparent: true,
                lights: true,
            });
            // 水面采样器
            material.uniforms['mirrorSampler'].value = renderTarget.texture;
            // 纹理矩阵
            material.uniforms['textureMatrix'].value = textureMatrix;
            material.uniforms['alpha'].value = alpha;
            material.uniforms['time'].value = time;
            // 法线采样器
            material.uniforms['normalSampler'].value = normalSampler;
            // 太阳颜色
            material.uniforms['sunColor'].value = sunColor;
            // 太阳方向
            material.uniforms['sunDirection'].value = sunDirection;
            material.uniforms['distortionScale'].value = distortionScale;
            material.uniforms['eye'].value = eye;
            material.uniforms['uFrequency'].value = new THREE.Vector2(50, 100);
            const waterPlane = new Mesh(obj.geometry, material);
            if (obj['name'].indexOf('生物池') !== -1) {
                waterPlane.color = new THREE.Color('#998261')
                material.uniforms['waterColor'].value = new THREE.Color('#998261');
            } else if (obj['name'].indexOf('二沉池') !== -1) {
                waterPlane.color = new THREE.Color('#6b9a95')
                material.uniforms['waterColor'].value = new THREE.Color('#6b9a95');
            } else if (obj['name'].indexOf('初沉池') !== -1) {
                waterPlane.color = new THREE.Color('#879d73')
                material.uniforms['waterColor'].value = new THREE.Color('#879d73');
            } else if (obj['name'].indexOf('沉淀池') !== -1) {
                waterPlane.color = new THREE.Color('#646c5a')
                material.uniforms['waterColor'].value = new THREE.Color('#646c5a');
            } else if (obj['name'].indexOf('滤池') !== -1) {
                waterPlane.color = new THREE.Color('#7b8584')
                material.uniforms['waterColor'].value = new THREE.Color('#7b8584');
            }
            waterPlane.renderOrder = 100;
            waterPlane.position.copy(obj.position);
            waterPlane.rotateX(-Math.PI / 2);
            waterPlane.name = obj.name;
            waterPlaneGroup.add(waterPlane);
        }
    })
}


export { createWaterPlane, waterPlaneGroup }

