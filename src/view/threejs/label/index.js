
import * as THREE from 'three';
// 引入CSS2D对象、CSS2D渲染器
import { CSS2DObject } from "three/examples/jsm/renderers/CSS2DRenderer";

// 人物CSS2D标签对象
let css2DPeopleLabel = null;
// 创建建筑标签组对象
const buildLabelGroup = new THREE.Group();

// 初始化标签，页面元素加载完成后调用，获取元素转换为CSS2D对象
function initLabel (model) {
    // 获取人物标签元素
    const peopleLabel = document.getElementById('peopleLabel');
    // 页面元素转换成CSS2D标签对象
    css2DPeopleLabel = new CSS2DObject(peopleLabel);
    css2DPeopleLabel.name = '人物模型标签';
    // 添加建筑标签
    addBuildLabel(model);
}

// 添加建筑标签
function addBuildLabel (model) {
    model.add(buildLabelGroup);
    // 获取所有建筑位置对象
    const buildPositionObj = model.getObjectByName('建筑物坐标');
    if (buildPositionObj) {
        buildPositionObj.children.map(obj => {
            // 获取并克隆建筑标签元素
            const buildLabel = document.getElementById('buildLabel').cloneNode(true);
            // 建筑标签元素转换成CSS2D标签对象
            const css2DBuildLabel = new CSS2DObject(buildLabel);
            // 设置建筑标签的建筑名称
            css2DBuildLabel.element.children[0].innerHTML = obj.name;
            // 设置建筑标签位置
            css2DBuildLabel.position.copy(obj.position);
            buildLabelGroup.add(css2DBuildLabel);
        })
    }
}
export { css2DPeopleLabel, initLabel, buildLabelGroup }
