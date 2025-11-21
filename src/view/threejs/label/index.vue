!<template>
  <!-- 人物标签 -->
  <div id="peopleLabel" style="display: none">
    <div>巡检员: 小王</div>
  </div>
  <!-- 建筑标签 -->
  <div id="buildLabel" style="display: none">
    <div class="name">建筑标签</div>
  </div>
</template>

<style lang="less" >
#peopleLabel {
  font-size: 0.7vw;
  width: 5vw;
  height: 3vh;
  line-height: 3vh;
  border: 0.2vh solid #1890ff;
  background: #405f80;
  box-shadow: inset 0px 0px 0.7vh 0.3vh #497fb8;
  font-family: "Times New Roman", Times, serif;
  font-weight: 600;
  div {
    display: flex;
    justify-content: center;
    align-items: center;
    color: #ffffe0;
  }
}
#buildLabel {
  background: url("../../../assets/shouye/buildLabel.png");
  background-size: 100% 100%;
  width: 8vw;
  height: 5vh;
  position: absolute;
  top: -1vw;
  left: 3vw;
  // z-index: 0;s

  .name {
    width: 5vw;
    text-align: center;
    line-height: 4.5vh;
    margin-left: 2.5vw;
    font-size: 0.7vw;
    font-family: Noto Sans S Chinese;
    font-weight: 500;
    color: #ffffff;
  }
}
</style>
