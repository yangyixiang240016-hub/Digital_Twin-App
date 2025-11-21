
// threejs 基础配置代码(场景、相机、灯光、渲染器等)

// 引入threejs
import * as THREE from 'three';
// 引入相机轨道控制器
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// 引入CSS2D渲染器
import { CSS2DRenderer } from "three/examples/jsm/renderers/CSS2DRenderer";
// 获取窗口宽高
const width = window.innerWidth;
const height = window.innerHeight;

// 创建场景
const scene = new THREE.Scene();

// 创建坐标轴辅助器
const axes = new THREE.AxesHelper(50);
axes.name = '坐标轴辅助器';
// scene.add(axes);

// 创建透视投影相机
const camera = new THREE.PerspectiveCamera(30, width / height, 1, 2000);
camera.name = '相机';
// camera.position.set(0.103, 179.349, 123.908);
camera.position.set(-10, 101.22038679129973, 692.9236288441222);
// camera.position.set(123.908, 179.349, 0.103);
camera.lookAt(0, 1.6, 0);

// 创建环境光
const ambientLight = new THREE.AmbientLight('#fff', 1.5);
ambientLight.name = '环境光';
scene.add(ambientLight);

// 创建平行光
const directionalLight1 = new THREE.DirectionalLight('#fff', 3);
directionalLight1.position.set(150, 120, -120);
scene.add(directionalLight1);

// 开启光源阴影的计算
directionalLight1.castShadow = true;
// 设置阴影像素
directionalLight1.shadow.mapSize.set(3000, 3000);
// 设置阴影边缘模糊半径
directionalLight1.shadow.radius = 1;
// 设置计算阴影的范围
directionalLight1.shadow.camera.left = -300;
directionalLight1.shadow.camera.right = 300;
directionalLight1.shadow.camera.top = 400;
directionalLight1.shadow.camera.bottom = -400;
directionalLight1.shadow.camera.near = 0.5;
directionalLight1.shadow.camera.far = 500;
directionalLight1.shadow.bias = -0.0002;

// 创建渲染器
const renderer = new THREE.WebGLRenderer({
    antialias: true,
});
// 设置像素比
renderer.setPixelRatio(window.devicePixelRatio);
// 定义渲染区域大小
renderer.setSize(width, height);
// 设置渲染器颜色输出方式
renderer.outputEncoding = 3001;
// 设置渲染器允许光源阴影渲染
renderer.shadowMap.enabled = true;
// 模型表面产生条纹影响渲染效果，可以改变.shadowMap.type默认值优化
renderer.shadowMap.type = THREE.VSMShadowMap;

// 创建CSS渲染器
const css2DRender = new CSS2DRenderer();
// 设置渲染宽高
css2DRender.setSize(window.innerWidth, window.innerHeight);
// HTML标签外面父元素叠加到canvas画布上且重合
css2DRender.domElement.style.position = 'absolute';
//具体值根据canvas画布位置来定
css2DRender.domElement.style.top = '0px';
//设置.pointerEvents=none，解决HTML元素标签对threejs canvas画布鼠标事件的遮挡
css2DRender.domElement.style.pointerEvents = 'none';

// 创建相机轨道控制器
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.6, 0);
// 设置相机控件旋转角度范围
controls.minPolarAngle = 0;
controls.maxPolarAngle = Math.PI / 2.2;
// 设置相机控件距离观察点的范围
// controls.minDistance = 100;
controls.maxDistance = 800;

// 设置界面跟随窗口自适应
window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    css2DRender.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
})
export { scene, camera, renderer, css2DRender, controls, directionalLight1 }

