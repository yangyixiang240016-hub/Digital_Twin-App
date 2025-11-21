<template>
  <div class="whole">
    <!-- threejs画布 -->
    <div id="threejs" ref="threejs"></div>
    <!-- 污水厂模型加载进度条 -->
    <a-progress
      :stroke-color="{
        from: '#00F5FF',
        to: '#4169E1',
      }"
      :percent="0.0"
      trailColor="#E8E8E8"
      status="active"
      class="progress"
    />
    <!-- 标签组件 -->
    <Label></Label>
    <!-- 巡检数据展示面板-->
    <div class="inspectPanel a-fadein" v-show="inspectPanelShow">
      <div class="panelTitle" id="panelTitle">曝气池</div>
      <div class="panelData">
        <div class="left">
          <div class="leftTitle">介绍</div>
          <div class="segment"></div>
          <div class="describe" id="describe"></div>
        </div>
        <div class="right">
          <div class="rightTitle">数据记录</div>
          <div class="segment"></div>
          <div class="record">
            <div class="main" id="panelData"></div>
          </div>
        </div>
      </div>
    </div>
    <!-- 巡检中 返回和状态按钮 -->
    <div class="inspect" v-show="props['selectedMenu'] === 'inspect'">
      <div class="common" @click="endInspect">
        <div class="return_icon" style=""></div>
        返回
      </div>
      <div class="common" @click="inspectStateChange">
        <div :class="inspectState ? 'stop_icon' : 'continue_icon'"></div>
        {{ inspectState ? "暂停" : "继续" }}
      </div>
    </div>
    <!-- 巡检进度条 -->
    <progressBar
      v-show="props['selectedMenu'] === 'inspect'"
      :schedule="schedule"
      :inspectState="inspectState"
      @progressBarChange="progressBarChange"
    ></progressBar>

    <!-- 巡检速度控制条 -->
    <speedControlBar
      v-show="props['selectedMenu'] === 'inspect'"
      :speed="speed"
      :inspectState="inspectState"
      @controlBarChange="controlBarChange"
    ></speedControlBar>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
// 引入threejs
import * as THREE from "three";
// 基础配置文件——场景、灯光、相机等
import {
  scene,
  renderer,
  css2DRender,
  camera,
  controls,
} from "./base/index.js";
// 添加污水厂模型函数
import { addSewageModel } from "./addSewageModel/index.js";
// 添加人物模型函数
import { addPeopleModel, WalkAction } from "./addPeopleModel/index.js";
// 引入tween.js,用来创建动画
import TWEEN from "@tweenjs/tween.js";
// 引入标签组件
import Label from "./label/index.vue";
// 引入人物2D标签、CSS2D渲染器、标签初始化函数和建筑标签组对象
import { css2DPeopleLabel, initLabel, buildLabelGroup } from "./label/index.js";
// 引入创建水面函数
import { createWaterPlane, waterPlaneGroup } from "./waterPlane/index.js";
import {
  inspectPathArr,
  inspectIndex,
  inspectPathIndex,
  inspectState,
  inspectPanelShow,
  inspectLinePointGroup,
  openInspection,
  inspectionParams,
} from "./inspection/index.js";
import progressBar from "./progressBar/index.vue";
import speedControlBar from "./speedControlBar/index.vue";
// 引入RGB加载器
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";
import { setPoolMaterial } from "./poolMaterial/index";
// 首页传值
const props = defineProps([
  "craftAnimationStatus", // 工艺动画状态，为true时开启播放相应的工艺动画
  "craftAnimationType", // 工艺动画类型，根据此值决定动画的类型
  "selectedMenu", // 首页底部菜单按钮选中项
]);
// 传递事件
const emit = defineEmits(["closeInspect", "craftAnimationEnd"]);

// threejs容器
const threejs = ref();
// 污水厂模型
let sewageModel = null;
// 人物模型
let people = null;
// 人物动画播放器
let animationMixer = null;
// 当前巡检进度百分比值
let schedule = ref(0);
// 巡检的速度
let speed = ref(0);

onMounted(async () => {
  threejs.value.appendChild(renderer.domElement);
  threejs.value.appendChild(css2DRender.domElement);
  const rgbeLoader = new RGBELoader();
  // 环境贴图
  let envMap = await rgbeLoader.loadAsync("./envMap.hdr");
  createEnvironment(envMap);
  // 异步加载污水厂模型
  sewageModel = await addSewageModel(envMap);
  // 添加人物模型、人物动画播放器
  const { peopleGroup, mixer } = await addPeopleModel();
  people = peopleGroup;
  // 相机添加到人物模型中
  people.add(camera);
  animationMixer = mixer;
  // 允许人物模型产生阴影
  people.castShadow = true;
  scene.add(sewageModel, people, inspectLinePointGroup);
  // 创建水面
  createWaterPlane(sewageModel, envMap);
  // 设置水池材质
  setPoolMaterial(sewageModel);
  // 开始循环渲染
  render();
  // 播放首次进入动画
  eventAnimation();
});

watch(
  () => props["craftAnimationStatus"],
  (e) => {
    if (e) {
      // 重置水面透明度
      waterPlaneGroup.children.map((obj) => {
        obj.material.uniforms.alpha.value = 1.0;
      });
      craftAnimation(props["craftAnimationType"]);
    }
  }
);
watch(
  () => props["selectedMenu"],
  (e) => {
    // 巡检开启
    if (e === "inspect") {
      // 相机角度重置
      camera.rotation.x = -0.9662198328141542;
      camera.rotation.y = 0.0004725006116027576;
      camera.rotation.z = 0.0006839146449353786;
      // 相机位置重置
      camera.position.set(0.103, 179.349, 123.908);
      // 相机观察点重置
      camera.lookAt(0, 1.7, 0);
      // 设置相机位置在人物模型后方
      camera.position.set(0, -5, -1);
      // camera.position.set(0, 1.4, -1);
      // 禁止相机控件旋转平移和缩放
      controls.enableRotate = false;
      controls.enablePan = false;
      controls.enableZoom = false;
      controls.target.set(0, 1.7, 0);
      controls.update();
      // 每次开启巡检时，将巡检项目索引和项目索引都重置，从第一个项目开始巡检
      inspectIndex.value = 0;
      inspectPathIndex.value = 0;
      // 人物步行动画开始播放
      WalkAction.play();
      // 人物标签开启显示
      css2DPeopleLabel.visible = true;
      // 巡检标线开启显示
      inspectLinePointGroup.children[inspectIndex.value].visible = true;
      // 建筑物标签关闭显示
      buildLabelGroup.children.map((item) => {
        item.visible = false;
      });
    } else if (e !== "craft") {
      // 相机角度重置
      camera.rotation.x = -0.9662198328141542;
      camera.rotation.y = 0.0004725006116027576;
      camera.rotation.z = 0.0006839146449353786;
      // 相机位置重置
      camera.position.set(0.103, 179.349, 123.908);
      // 相机观察点重置
      camera.lookAt(0, 0, 0);
      controls.target.set(0, 0, 0);
      controls.update();
      // 重置水面透明度水面颜色
      waterPlaneGroup.children.map((obj) => {
        obj.material.uniforms.alpha.value = 1.0;
        obj.material.uniforms.waterColor.value = obj.color;
      });
    }
  }
);

const clock = new THREE.Clock();
// 设置渲染帧率30FPS,默认情况下requestAnimationFrame在60帧左右，控制帧率优化性能
const FPS = 30;
// 间隔多长时间渲染一次
const renderT = 1 / FPS;
// 执行一次renderer.render，timeS重新置0
let timeS = 0;
// 渲染循环
function render() {
  //console.log(camera, "pos");
  // 循环渲染
  renderer.render(scene, camera);
  // 获取两帧渲染间隔时间
  const T = clock.getDelta();
  timeS = timeS + T;
  animationMixer.update(T);
  if (timeS > renderT) {
    TWEEN.update();
    // renderer.render每执行一次，timeS置0
    timeS = 0;
    // css2D标签渲染
    css2DRender.render(scene, camera);
    // 水面波纹动画渲染
    waterPlaneGroup.children.map((item) => {
      item.material.uniforms["time"].value += T / 6;
    });

    // 巡检时标线和拐点动画
    if (
      inspectLinePointGroup.children[inspectIndex.value] &&
      props["selectedMenu"] === "inspect"
    ) {
      inspectLinePointGroup.children[inspectIndex.value].children.map(
        (item) => {
          if (item.name === "标线") {
            item.material.map.offset.x -= 0.03;
          } else if (item.name === "拐点") {
            item.rotation.y += 0.02;
          }
        }
      );
    }
    // 巡检动画
    if (props["selectedMenu"] === "inspect" && inspectState.value) {
      openInspection(people, controls);
      schedule.value = inspectPathIndex.value;
      // 巡检速度不断更新
      if (inspectPathArr[inspectIndex.value]) {
        speed.value = inspectPathArr[inspectIndex.value].speed;
      }
      //console.log("巡检动画");
    }
  }
  requestAnimationFrame(render);
}
// 巡检状态变化事件
function inspectStateChange() {
  // 巡检的状态切换
  inspectState.value = !inspectState.value;
  // 关闭巡检数据面板的显示
  inspectPanelShow.value = false;
  if (inspectState.value) {
    // 人物动画开始播放
    WalkAction.play();
    if (inspectPathIndex.value >= 100) {
      // 巡检项目索引加1
      inspectIndex.value += 1;
      // 巡检标记线组对象开启显示
      inspectLinePointGroup.children.map((item, index) => {
        if (index === inspectIndex.value) {
          item.visible = true;
        } else {
          item.visible = false;
        }
      });
    }
  } else {
    // 人物动画停止播放
    WalkAction.stop();
  }
  if (inspectPathIndex.value >= 100) {
    // 巡检项目路径索引重新置零
    inspectPathIndex.value = 0;
  }
  // 巡检项目索引值超过巡检路径数组时，表示已经巡检完最后一项，调用endInspect()结束巡检
  if (inspectIndex.value > inspectPathArr.length - 1) {
    endInspect();
  }
}
// 结束巡检
function endInspect() {
  // 人物位置重置
  people.position.set(0, 0, 0);
  // 人物角度重置
  people.rotation.y = 0;
  people.rotation.x = 0;
  people.rotation.z = 0;
  // 相机位置重置
  camera.position.set(0.103, 179.349, 123.908);
  // 开启相机控件旋转平移和缩放
  controls.enableRotate = true;
  controls.enablePan = true;
  controls.enableZoom = true;
  // 相机控件观察点重置
  controls.target.set(0, 1.7, 0);
  // 相机控件更新
  controls.update();
  // 巡检状态重置为true
  inspectState.value = true;
  // 关闭巡检数据面板显示
  inspectPanelShow.value = false;
  // 人物标签隐藏显示
  css2DPeopleLabel.visible = false;
  // 巡检标记线组对象隐藏显示
  inspectLinePointGroup.children.map((item) => {
    item.visible = false;
  });
  // 建筑物标签开启显示
  buildLabelGroup.children.map((item) => {
    item.visible = true;
  });
  // 巡检速度重置
  inspectPathArr.map((item) => {
    item.speed = inspectionParams[item.name].speed;
  });

  // 关闭巡检
  emit("closeInspect");
}
// 巡检进度条变化事件
function progressBarChange(e) {
  // 检查是否是暂停/恢复事件
  if (typeof e === "object" && e.action) {
    if (e.action === "pause") {
      inspectState.value = false;
    } else if (e.action === "resume") {
      inspectState.value = true;
    }
  } else {
    // 原有的进度值更新逻辑
    inspectPathIndex.value = e;
  }
}
// 巡检速度条变化事件
function controlBarChange(e) {
  // 检查是否是暂停/恢复事件
  if (typeof e === "object" && e.action) {
    if (e.action === "pause") {
      inspectState.value = false;
    } else if (e.action === "resume") {
      inspectState.value = true;
    }
  } else {
    // 原有的速度值更新逻辑
    inspectPathArr[inspectIndex.value].speed = 0.4 * (e * 0.01);
  }
}
// 工艺动画
function craftAnimation(type) {
  // 重置水面透明度水面颜色
  waterPlaneGroup.children.map((obj) => {
    obj.material.uniforms.alpha.value = 1.0;
    obj.material.uniforms.waterColor.value = obj.color;
  });
  // 禁止相机控件旋转平移和缩放
  // controls.enableRotate = false;
  // controls.enablePan = false;
  // controls.enableZoom = false;
  // 精确曝气动画
  if (type === "aeration") {
    const name = "南北生物池水面";
    // 水面世界坐标位置
    const position = sewageModel
      .getObjectByName(name)
      .getWorldPosition(new THREE.Vector3());
    // 开启动画，视角切换到水面处
    new TWEEN.Tween(camera.position)
      .to({ x: -113.85, y: 7.67, z: 43.59 }, 1500)
      .easing(TWEEN.Easing.Sinusoidal.InOut)
      .onUpdate(() => {
        controls.target.copy(new THREE.Vector3(-113, 2, 30));
        controls.update();
      })
      // 动画执行完成后
      .onComplete(() => {
        // 获取水面模型
        const waterPlane = waterPlaneGroup.getObjectByName(name);
        // 加载气泡纹理
        const texture = new THREE.TextureLoader().load("./bubbles.png");
        // 球体(气泡)材质，map气泡贴图模仿气泡效果
        const material = new THREE.MeshPhysicalMaterial({
          map: texture,
          color: "#fff",
          transparent: true,
          opacity: 0.6,
        });
        // 球体(气泡)组对象
        const sphereGroup = new THREE.Group();
        // 创建box3包围盒计算水面模型尺寸
        const box3 = new THREE.Box3();
        box3.expandByObject(waterPlane);
        // 根据水面尺寸计算出球体(气泡)出现的范围
        const x = ((box3.max.x - box3.min.x) / 2).toFixed(3) - "";
        const z = ((box3.max.z - box3.min.z) / 2).toFixed(3) - "" - 0.1;
        // 循环创建多个球体(气泡)
        for (let i = 0; i <= 2000; i++) {
          // 指定随机大小创建球形几何体
          const sphere = new THREE.SphereGeometry(Math.random() * 0.03 + 0.05);
          const mesh = new THREE.Mesh(sphere, material);
          // 随机旋转一定角度
          mesh.rotateX(Math.random() * Math.PI);
          // 设置位置
          mesh.position.copy(position);
          // y值置空
          mesh.position.y = 0;
          // 随机在增加一定值，使气泡在不同的位置出现
          mesh.position.x += Math.random() * (x - -x) + -x;
          mesh.position.y += Math.random() * 2;
          mesh.position.z += Math.random() * (z - -z) + -z;
          // 随机气泡上升的速度值
          mesh.speed = Math.random() * 0.04 + 0.04;
          sphereGroup.add(mesh);
        }
        scene.add(sphereGroup);
        // 此变量用作循环动画和销毁动画
        let bubbleRiseAnimationId;
        // 气泡上升动画
        function bubbleRise() {
          bubbleRiseAnimationId = requestAnimationFrame(bubbleRise);
          sphereGroup.children.map((item) => {
            item.position.y += item.speed;
            if (item.position.y >= position.y) item.position.y = 0;
          });
        }
        bubbleRise();
        // 水面默认的透明度
        let alpha = waterPlane.material.uniforms.alpha.value;
        const color1 = new THREE.Color("#87CEFA");
        const color2 = waterPlane.material.uniforms.waterColor.value;
        // 此变量用作循环动画和销毁动画
        let waterPlaneAnimationId;
        // 水面逐渐透明动画
        function waterPlaneTransparent() {
          waterPlaneAnimationId = requestAnimationFrame(waterPlaneTransparent);
          // 透明度大于0.3则不断降低透明度
          if (alpha >= 0.3) {
            alpha -= 0.01;
            waterPlane.material.uniforms.alpha.value = alpha;
            const newColor = color1.clone().lerp(color2.clone(), alpha);
            waterPlane.material.uniforms.waterColor.value = newColor;
          }
          // 透明度小于0.3
          else {
            // 延迟一定秒数后移除气泡组对象
            setTimeout(() => {
              // scene.remove(sphereGroup);
            }, 3000);
            // 传递事件告知动画执行完毕
            emit("craftAnimationEnd");
            // 销毁水面透明动画和气泡上升动画
            cancelAnimationFrame(waterPlaneAnimationId);
            // cancelAnimationFrame(bubbleRiseAnimationId);
          }
        }
        waterPlaneTransparent();
      })
      .start();
  }
  // 精确加药
  if (type === "dosing") {
    const name = "东加药管2-2";
    // 加药管位置
    const position = sewageModel
      .getObjectByName(name)
      .getWorldPosition(new THREE.Vector3());
    // 将位置偏移一下到出水口
    position.y -= 0.138;
    position.z += 0.22;
    // 开启Tweenjs动画，将视角切换到加药管处
    new TWEEN.Tween(camera.position)
      .to({ x: 57.16, y: 2.09, z: 6.53 }, 1500)
      .easing(TWEEN.Easing.Sinusoidal.InOut)
      .onUpdate(() => {
        controls.target.copy(position);
        controls.update();
      })
      // 视角切换完成后
      .onComplete(() => {
        // 创建一个位置数组，因为这个加药管有多个出水口，每个位置对应一个出水口
        const posArr = [];
        // 当前出水口位置先push到数组里去
        posArr.push(position);
        // 获取左侧出水口位置
        for (let i = 1; i <= 4; i++) {
          const pos = position.clone();
          pos.x += i * 0.765;
          posArr.push(pos);
        }
        // 获取右侧出水口位置
        for (let i = 1; i <= 4; i++) {
          const pos = position.clone();
          pos.x -= i * 0.765;
          posArr.push(pos);
        }
        // 创建球形几何体，模仿水滴
        const sphereGeometry = new THREE.SphereGeometry(0.005, 16, 16);
        const sphereMaterial = new THREE.MeshPhongMaterial({
          color: "#afeeee",
        });
        // 创建球体数组，存储所有的球体
        const sphereArr = [];
        // 每个出水管球体数量
        const numSpheres = 300;
        // 遍历posArr位置数组，给每个出水管创建球体
        posArr.map((pos) => {
          for (let i = 0; i < numSpheres; i++) {
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            // 默认将其隐藏起来，因为随机高度球体会高于出水管
            sphere.visible = false;
            // 赋值出水管位置
            sphere.position.copy(pos);
            // 球体高度在加上一个随机值
            sphere.position.y += Math.random() * 2; // 不同的初始高度
            // 设置球体下落速度
            sphere.velocity = Math.random() * 0.02 + 0.01; // 随机下落速度
            sphereArr.push(sphere);
            scene.add(sphere);
          }
        });
        // 此变量用作循环动画和销毁动画
        let animationFrameId1;
        function animation1() {
          animationFrameId1 = requestAnimationFrame(animation1);
          // 遍历球体数组
          sphereArr.forEach((sphere) => {
            if (sphere.position.y <= position.y) {
              sphere.visible = true;
            }
            sphere.position.y -= sphere.velocity;
            if (sphere.position.y <= 0.3) {
              // 当球体下落到一定位置时
              sphere.position.y = position.y; // 重新置于顶端
            }
          });
        }
        animation1();

        const waterPlane =
          waterPlaneGroup.getObjectByName("东西生物池-东水面1");
        let alpha = waterPlane.material.uniforms.alpha.value;

        const color1 = new THREE.Color("#87CEFA");
        const color2 = waterPlane.material.uniforms.waterColor.value;
        // 此变量用作循环动画和销毁动画
        let animationFrameId2;
        function animation2() {
          animationFrameId2 = requestAnimationFrame(animation2);
          if (alpha >= 0.5) {
            alpha -= 0.006;
            waterPlane.material.uniforms.alpha.value = alpha;
            const newColor = color1.clone().lerp(color2.clone(), alpha);
            waterPlane.material.uniforms.waterColor.value = newColor;
          } else {
            emit("craftAnimationEnd");
            cancelAnimationFrame(animationFrameId2);
          }
        }
        animation2();
      })
      .start();
  }
  // 污泥回流
  if (type === "sludge") {
    // 二沉池模型名称数组
    const sinkPoolNameArr = [
      "二沉池3水面",
      "二沉池3水面001",
      "二沉池4水面",
      "二沉池4水面001",
      // "初沉池水面1",
      // "初沉池水面1001",
    ];
    // 生物池模型名称数组
    const organismPoolNameArr = [
      "南北生物池水面",
      "东西生物池-东水面1",
      "东西生物池-东水面2",
      "东西生物池-西水面1",
      "东西生物池-西水面2",
    ];

    // 获取二沉池模型
    const sinkPoolArr = [];
    sinkPoolNameArr.map((name) => {
      sinkPoolArr.push(waterPlaneGroup.getObjectByName(name));
    });

    // 获取生物池模型
    const organismPoolArr = [];
    organismPoolNameArr.map((name) => {
      const organismPool = waterPlaneGroup.getObjectByName(name);
      organismPool.material.uniforms.alpha.value = 0.3;
      organismPool.visible = false;
      organismPool.userData.y = organismPool.clone().position.y;
      organismPool.position.y = 0;
      organismPoolArr.push(organismPool);
    });

    //  x: -10.84, y: 289.89, z: 276.17
    // 开启动画，视角切换到整个污水厂
    new TWEEN.Tween(camera.position)
      .to({ x: 100, y: 100, z: 180 }, 1500)
      .easing(TWEEN.Easing.Sinusoidal.InOut)
      .onUpdate(() => {
        controls.target.set(100, 0, -30);
        controls.update();
      })
      .onComplete(() => {
        // 此变量用作循环动画和销毁动画
        let waterPlaneAnimationId;
        // 水面逐渐透明动画
        function waterPlaneTransparent() {
          waterPlaneAnimationId = requestAnimationFrame(waterPlaneTransparent);
          sinkPoolArr.map((item) => {
            let alpha = item.material.uniforms.alpha.value;
            // 透明度大于0.3则不断降低透明度
            if (alpha >= 0.3) {
              alpha -= 0.01;
              item.material.uniforms.alpha.value = alpha;
            }
          });

          if (
            sinkPoolArr[sinkPoolArr.length - 1].material.uniforms.alpha.value <
            0.3
          ) {
            // 传递事件告知动画执行完毕
            // emit("craftAnimationEnd");
            cancelAnimationFrame(waterPlaneAnimationId);
            waterLevelRise();
          }
        }
        waterPlaneTransparent();

        // 此变量用作循环动画和销毁动画
        let waterLevelRiseAnimationId;
        function waterLevelRise() {
          waterLevelRiseAnimationId = requestAnimationFrame(waterLevelRise);
          organismPoolArr.map((item) => {
            item.visible = true;
            const yPos = item.userData.y;
            let alpha = item.material.uniforms.alpha.value;
            if (item.position.y < yPos) {
              item.position.y += 0.01;
            }

            if (alpha < 1) {
              alpha += 0.02;
              item.material.uniforms.alpha.value = alpha;
            }

            if (item.position.y >= yPos && alpha >= 1) {
              // 传递事件告知动画执行完毕
              emit("craftAnimationEnd");
              cancelAnimationFrame(waterLevelRiseAnimationId);
            }
          });
        }
      })
      .start();
  }
}
// 首次进入动画
function eventAnimation() {
  new TWEEN.Tween(camera.position)
    .to({ x: 0.103, y: 179.349, z: 123.908 }, 2000)
    .easing(TWEEN.Easing.Sinusoidal.InOut)
    .onUpdate(() => {
      controls.target.set(0, 0, 0);
      controls.update();
    })
    .onComplete(() => {
      // 初始化标签
      initLabel(sewageModel);
      // 将人物标签添加到人物模型中
      people.children[0].add(css2DPeopleLabel);
      // 设置位置在人物模型头顶
      css2DPeopleLabel.position.set(0, 2.2, 0);
      // 设置合适大小
      css2DPeopleLabel.scale.set(0.1, 0.1, 0.1);
      // 人物标签默认隐藏显示
      css2DPeopleLabel.visible = false;
    })
    .start();
}
function createEnvironment(texture) {
  // scene.environment = texture;
  // hdr作为环境贴图生效，设置.mapping为EquirectangularReflectionMapping
  texture.mapping = THREE.EquirectangularReflectionMapping;
  // 创建一个巨大球体作为整个天空环境
  const sphere = new THREE.SphereGeometry(1000, 512, 512);
  const material = new THREE.MeshBasicMaterial({
    map: texture,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(sphere, material);
  mesh.position.y -= 100;
  scene.add(mesh);
}
</script>
<style lang="less">
@import "./index.less";
</style>
