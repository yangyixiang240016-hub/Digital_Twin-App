// 引入threejs
import * as THREE from "three";
import { ref, onMounted, watch, reactive } from "vue";
import { WalkAction } from "../addPeopleModel/index.js";
// import CSG from 'three-csg';
import { CSG } from "three-csg-ts";
// 巡检路径数组，用来存储巡检时所用的曲线路径，格式[巡检1曲线路径,巡检2曲线路径...]
const inspectPathArr = reactive([]);
// 巡检项目索引，表示当前巡检到第几项
const inspectIndex = ref(0);
// 巡检项目路径索引,表示在某一项巡检中的某个路径位置索引
const inspectPathIndex = ref(0);
// 巡检的状态-暂停或继续
const inspectState = ref(true);
// 巡检数据面板显示
const inspectPanelShow = ref(false);
// 巡检中的标线和拐点总对象
const inspectLinePointGroup = new THREE.Group();

// 箭头指示纹理贴图
const arrowTexture = new THREE.TextureLoader().load("./arrow.png");
arrowTexture.wrapS = THREE.RepeatWrapping;
arrowTexture.wrapT = THREE.RepeatWrapping;

// 巡检项目的路径数据对象
const inspectionPathDataObj = {
  曝气池: [
    new THREE.Vector3(-82, -0.05, -40.5),
    new THREE.Vector3(-82, -0.05, -6),
    new THREE.Vector3(-68.5, -0.05, -6),
    new THREE.Vector3(-68.5, -0.05, 37.5),
    new THREE.Vector3(-78.5, -0.05, 37.5),
    new THREE.Vector3(-78.5, -0.05, 40),
    new THREE.Vector3(-75, 1.4, 40),
    new THREE.Vector3(-75, 1.4, 39.4),
    new THREE.Vector3(-77.5, 2.6, 39.4),
    new THREE.Vector3(-77.5, 2.6, 40),
    new THREE.Vector3(-74.5, 3.7, 40),
    new THREE.Vector3(-74.5, 3.7, 42),
  ],
  鼓风机房: [
    new THREE.Vector3(-82, -0.05, -40.5),
    new THREE.Vector3(-82, -0.05, -6),
    new THREE.Vector3(1, -0.05, -6),
    new THREE.Vector3(1, -0.05, -14),
  ],
  二沉池: [
    new THREE.Vector3(-82, -0.05, -40.5),
    new THREE.Vector3(-82, -0.05, -53),
    new THREE.Vector3(-63.5, -0.05, -73),
    new THREE.Vector3(-63.5, -0.05, -73),
    new THREE.Vector3(109.7, -0.05, -72),
    new THREE.Vector3(109.7, -0.05, -46),
    new THREE.Vector3(104, -0.05, -46),
    new THREE.Vector3(104, -0.05, -43.5),
    new THREE.Vector3(106, 0.6, -43.5),
  ],
  粗格栅: [
    new THREE.Vector3(-82, -0.05, -40.5),
    new THREE.Vector3(-82, -0.05, -6),
    new THREE.Vector3(-68.5, -0.05, -6),
    new THREE.Vector3(-68.5, -0.05, 62.5),
    new THREE.Vector3(-75, -0.05, 62.5),
    new THREE.Vector3(-75, 1.4, 59.6),
    new THREE.Vector3(-74.3, 1.4, 59.6),
    new THREE.Vector3(-74.3, 2.55, 61.8),
    new THREE.Vector3(-75, 2.55, 61.8),
    new THREE.Vector3(-75, 3.75, 60),
    new THREE.Vector3(-75, 3.75, 58.7),
    new THREE.Vector3(-78, 3.75, 58.7),
    new THREE.Vector3(-78, 3.75, 59),
  ],
};
const inspectionParams = {
  鼓风机房: {
    speed: 0.1,
    describe:
      "鼓风机房是用于存放鼓风机的建筑物。鼓风机用来给生化好氧菌提供氧气，即曝气过程。变配电间是电力网中的线路连接点，是用以变换电压、交换功率和汇集、分配电能的设施。它是电网的重要组成部分和电能传输的重要环节，对保证电网安全、经济运行具有举足轻重的作用。",
    data: [
      ["1#鼓风机频率反馈", "0.0282HZ"],
      ["2#鼓风机频率反馈", "0.0000HZ"],
      ["3#鼓风机频率反馈", "44.0234HZ"],
      ["出风管流量计：瞬时流量", "1500.4323m³/d"],
      ["出风管流量计：累计流量", "21687432m³/d"],
      ["鼓风机房总管压力", "0.0848MPa"],
    ],
  },
  二沉池: {
    speed: 0.05,
    describe:
      "污水经过水解酸化池及AAO生化池后进去二沉池，二沉池的作用是泥水分离，使混合渣澄清、活性污泥浓缩并将分离的小部分污泥送去污泥脱水工段，大部分污泥通过污泥回流泵泵送回曝气池，用于调节生物池污泥浓度，保持生化池稳定运行。",
    data: [["污泥回流泵池液位", "5.3847m"]],
  },
  粗格栅: {
    speed: 0.05,
    describe:
      "粗格栅将污水中较大漂浮物和悬浮物截留，减少后续处理产生的浮渣，防止堵塞污水处理设施，保证后续流程正常运行。经过粗格栅过滤的水在进水泵中再一次提升高度，便于其流入细格栅及沉沙池中。",
    data: [
      ["进水COD", "59.8597mg/L"],
      ["进水氨氮", "13.4187/L"],
      ["进水总磷", "0.0000mg/L"],
      ["进水总氮", "0.0000mg/L"],
      ["进水pH", "7.1028"],
      ["进水瞬时流量", "234.5378/h"],
      ["进水累计流量", "3006253m³/d"],
      ["出水COD", "59.8597mg/L"],
      ["出水氨氮", "13.4187/L"],
      ["出水总磷", "0.0000mg/L"],
      ["出水总氮", "0.0000mg/L"],
      ["出水pH", "7.1028"],
      ["出水瞬时流量", "234.5378/h"],
      ["出水累计流量", "3006253m³/d"],
    ],
  },
  曝气池: {
    speed: 0.2,
    describe:
      "污水通过曝气氧化池进入昭气生物源池，曝气生物滤池最高液位5.9米，有效溶剂3200立方米实现生物降解有机物，硝化、反硝化及截留悬浮物于一体，进一步去除污水中的COD、氨氮及悬浮物后流入下一处理单元--转盘滤池",
    data: [
      ["硝化液回流流量", "0.362m3/h"],
      ["硝化与反硝化：反冲洗风管压力", "0.1362m3/h"],
      ["硝化与反硝化：DC滤池5#DO", "2.2362m3/h"],
      ["硝化与反硝化：DC滤池6#DO", "5.3465m3/h"],
      ["硝化与反硝化：反冲洗管流量", "0.3765m3/h"],
      ["硝化与反硝化：反冲洗风管流量", "0.4522m3/h"],
      ["硝化与反硝化：DC滤池1#DO", "2.2472m3/h"],
      ["硝化与反硝化：DC滤池2#DO", "6.2735m3/h"],
      ["硝化与反硝化：DC滤池3#DO", "3.5323m3/h"],
      ["硝化与反硝化：DC滤池4#DO", "7.5932m3/h"],
      ["硝化与反硝化：DC滤池7#DO", "3.1348m3/h"],
    ],
  },
};
// 顶点着色器代码
const vertexShader = `
    varying vec2 vUv;
    void main(){
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
    }
`;
// 片元着色器代码
const fragmentShader = `
    uniform float uTime;
    varying vec2 vUv;
    void main(){
        vec3 color1 = vec3(0.0,0.913,1.0);
        vec3 color2 = vec3(1.0,1.0,0.0);
        vec3 mixer = mix(color1,color2,step(0.5, fract(vUv.x * 6.0)));
        gl_FragColor = vec4(mixer,0.7);
    }
`;
// 半圆面材质
const semiCircleMaterial = new THREE.ShaderMaterial({
  vertexShader: vertexShader,
  fragmentShader: fragmentShader,
  side: THREE.DoubleSide,
  transparent: true,
});
// 要减去的几何体
const boxGeometry = new THREE.BoxGeometry(1.2, 0.5, 1.2);
const boxMesh = new THREE.Mesh(boxGeometry, semiCircleMaterial);
boxMesh.position.y += 0.6;
boxMesh.updateMatrix(); // 更新几何体的矩阵
// 半圆体
const semiCircleGeometry = new THREE.SphereGeometry(
  0.5,
  16,
  16,
  0,
  Math.PI * 2,
  0,
  Math.PI / 2
);
const semiCircleMesh = new THREE.Mesh(semiCircleGeometry);
// 使用CSG方法执行相减运算，得出一个上部分被截去半圆面
const subtractedGeometry = CSG.subtract(semiCircleMesh, boxMesh);
// 裁剪去大致的顶部顶点，使半圆面呈现镂空效果
let posArr = [...subtractedGeometry.geometry.attributes.position.array];
posArr = posArr.slice(0, 2460);
subtractedGeometry.geometry.attributes.position.array = new Float32Array(
  posArr
);
const subtractMesh = new THREE.Mesh(
  subtractedGeometry.geometry,
  semiCircleMaterial
);
subtractMesh.updateMatrix(); // 更新几何体的矩阵

// 遍历巡检项目对象，创建巡检路径数组、巡检道路、巡检位置标记
for (let item in inspectionPathDataObj) {
  // 创建曲线路径
  const curvePath = new THREE.CurvePath();
  curvePath.name = item;
  curvePath.speed = inspectionParams[item].speed;
  curvePath.describe = inspectionParams[item].describe;
  curvePath.data = inspectionParams[item].data;
  const currentPathArr = inspectionPathDataObj[item];
  // 创建一个组对象，存储当前巡检项目的标线和拐点
  const currentLinePointArr = new THREE.Group();
  currentLinePointArr.visible = false;
  inspectLinePointGroup.add(currentLinePointArr);
  currentPathArr.map((currentPos, index) => {
    const cloneMesh = subtractMesh.clone();
    cloneMesh.position.copy(currentPos);
    cloneMesh.name = "拐点";
    cloneMesh.renderOrder = index;
    currentLinePointArr.add(cloneMesh);

    if (index < currentPathArr.length - 1) {
      // 下一个位置点
      const nextPos = currentPathArr[index + 1];
      // 创建三维曲线
      const line3 = new THREE.LineCurve3(currentPos, nextPos);
      curvePath.curves.push(line3);
      // 计算出当前点距离到下一个点的距离
      const distance = currentPos.distanceTo(nextPos.clone());
      // 创建平面几何体
      const plane = new THREE.PlaneGeometry(distance, 1);
      // 克隆箭头指示纹理贴图
      const texture = arrowTexture.clone();
      // 根据距离设置箭头指示贴图x轴阵列数
      texture.repeat.x = distance / 2;
      // 创建材质，设置箭头指示纹理
      const material = new THREE.MeshBasicMaterial({
        map: texture,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.7,
        color: "#00ffff",
        // depthWrite: false,
        // depthTest: false,
      });
      // 标线模型
      const lineMesh = new THREE.Mesh(plane, material);
      lineMesh.name = "标线";
      lineMesh.renderOrder = 1;
      lineMesh.position.copy(currentPos);
      // 计算偏差，因为标线的位置还在currentPos这个起始处，需要加上到nextPos位置的一半值
      const deviation = nextPos.clone().sub(currentPos).divideScalar(2);
      lineMesh.position.add(deviation);
      // 方向值
      const direction = nextPos.clone().sub(currentPos).normalize();
      direction.add(lineMesh.position);
      lineMesh.lookAt(direction);
      lineMesh.rotateX(-Math.PI / 2);
      lineMesh.rotateZ(-Math.PI / 2);
      lineMesh.position.y -= 0.02;
      currentLinePointArr.add(lineMesh);
    }
  });
  inspectPathArr.push(curvePath);
}
//
function openInspection(people, controls) {
  // 当前巡检路径
  const currentPath = inspectPathArr[inspectIndex.value];
  if (currentPath) {
    // 曲线路径上的百分比值，表示人物当前走到这段路径的比值
    const ratio = inspectPathIndex.value / 100;
    // 通过比值在曲线中获取位置
    const pos = currentPath.getPoint(ratio);
    // 将比值往前调一点，可以防止人物模型转向的延迟
    const futureRatio = Math.min(ratio + 0.005, 1);
    // 获取当前曲线位置上的切线
    const tangent = currentPath.getTangentAt(futureRatio);
    // 忽略y分量，保持人物垂直
    tangent.y = 0;
    // 当前人物朝向
    const lookAtPoint = pos.clone().add(tangent);
    people.lookAt(lookAtPoint);
    // 更新人物模型位置
    people.position.copy(pos);
    // 更新相机控件观测点
    controls.target.copy(pos);
    controls.target.y += 1.4;
    inspectPathIndex.value += currentPath.speed;
    // 当人物在该路径上走完时
    if (inspectPathIndex.value >= 100) {
      // 巡检进入暂停状态，开始展示巡检数据
      inspectState.value = false;
      // 显示巡检数据面板
      inspectPanelShow.value = true;
      // 停止人物模型步行动画播放
      WalkAction.stop();
      // 巡检数据面板标题更新
      document.getElementById("panelTitle").innerHTML = currentPath.name;
      // 巡检数据面板描述内容更新
      document.getElementById("describe").innerHTML = currentPath.describe;
      // 巡检数据面板数据更新
      let panelDataStr = "";
      currentPath.data.map((item) => {
        panelDataStr += `
                        <div class="row">
                            <div>${item[0]}</div>
                            <div>${item[1]}</div>
                        </div>
                    `;
      });
      document.getElementById("panelData").innerHTML = panelDataStr;
    }
  }
}

export {
  inspectPathArr,
  inspectIndex,
  inspectPathIndex,
  inspectState,
  inspectPanelShow,
  inspectLinePointGroup,
  openInspection,
  inspectionParams,
};
