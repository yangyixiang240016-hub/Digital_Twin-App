# Details

Date : 2025-11-18 15:35:24

Directory c:\\Users\\59790\\Desktop\\污水处理厂源码

Total : 133 files,  38707 codes, 1736 comments, 4442 blanks, all 44885 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.env](/.env) | Properties | 2 | 0 | 2 | 4 |
| [AAO 接口调用 - 联调.http](/AAO%20%E6%8E%A5%E5%8F%A3%E8%B0%83%E7%94%A8%20-%20%E8%81%94%E8%B0%83.http) | HTTP | 342 | 48 | 91 | 481 |
| [README.md](/README.md) | Markdown | 4 | 0 | 4 | 8 |
| [backend/app.py](/backend/app.py) | Python | 15 | 1 | 6 | 22 |
| [backend/models/tdengine.py](/backend/models/tdengine.py) | Python | 60 | 1 | 9 | 70 |
| [backend/requirements.txt](/backend/requirements.txt) | pip requirements | 3 | 0 | 1 | 4 |
| [backend/routes/__init__.py](/backend/routes/__init__.py) | Python | 21 | 7 | 2 | 30 |
| [backend/routes/data_clean.py](/backend/routes/data_clean.py) | Python | 190 | 12 | 39 | 241 |
| [backend/routes/history_data.py](/backend/routes/history_data.py) | Python | 167 | 12 | 36 | 215 |
| [backend/routes/inflow.py](/backend/routes/inflow.py) | Python | 10 | 0 | 3 | 13 |
| [backend/routes/offline.py](/backend/routes/offline.py) | Python | 109 | 13 | 33 | 155 |
| [backend/routes/offline_result.py](/backend/routes/offline_result.py) | Python | 526 | 28 | 92 | 646 |
| [backend/routes/outflow.py](/backend/routes/outflow.py) | Python | 10 | 0 | 2 | 12 |
| [backend/routes/system_params.py](/backend/routes/system_params.py) | Python | 102 | 1 | 19 | 122 |
| [backend/routes/trend.py](/backend/routes/trend.py) | Python | 11 | 0 | 3 | 14 |
| [backend/routes/water_quality.py](/backend/routes/water_quality.py) | Python | 47 | 6 | 8 | 61 |
| [backend/services/data_clean_service.py](/backend/services/data_clean_service.py) | Python | 279 | 37 | 42 | 358 |
| [backend/services/history_data_service.py](/backend/services/history_data_service.py) | Python | 281 | 37 | 51 | 369 |
| [backend/services/inflow_service.py](/backend/services/inflow_service.py) | Python | 7 | 0 | 2 | 9 |
| [backend/services/offline_result_service.py](/backend/services/offline_result_service.py) | Python | 1,233 | 163 | 242 | 1,638 |
| [backend/services/offline_service.py](/backend/services/offline_service.py) | Python | 146 | 6 | 16 | 168 |
| [backend/services/outflow_service.py](/backend/services/outflow_service.py) | Python | 7 | 0 | 2 | 9 |
| [backend/services/system_params_service.py](/backend/services/system_params_service.py) | Python | 339 | 18 | 43 | 400 |
| [backend/services/trend_service.py](/backend/services/trend_service.py) | Python | 326 | 46 | 59 | 431 |
| [backend/services/water_quality_service.py](/backend/services/water_quality_service.py) | Python | 139 | 15 | 11 | 165 |
| [dbpkg/AccessDB.py](/dbpkg/AccessDB.py) | Python | 359 | 42 | 76 | 477 |
| [dbpkg/DBBase.py](/dbpkg/DBBase.py) | Python | 69 | 6 | 19 | 94 |
| [dbpkg/SQLServerDB.py](/dbpkg/SQLServerDB.py) | Python | 398 | 51 | 88 | 537 |
| [dbpkg/TDengineDB.py](/dbpkg/TDengineDB.py) | Python | 620 | 82 | 109 | 811 |
| [dbpkg/__init__.py](/dbpkg/__init__.py) | Python | 19 | 2 | 7 | 28 |
| [dbpkg/config.ini](/dbpkg/config.ini) | Ini | 37 | 0 | 4 | 41 |
| [dbpkg/settings.py](/dbpkg/settings.py) | Python | 197 | 32 | 39 | 268 |
| [index.html](/index.html) | HTML | 13 | 0 | 2 | 15 |
| [package-lock.json](/package-lock.json) | JSON | 4,111 | 0 | 1 | 4,112 |
| [package.json](/package.json) | JSON | 33 | 0 | 1 | 34 |
| [public/vite.svg](/public/vite.svg) | XML | 1 | 0 | 0 | 1 |
| [src/App.vue](/src/App.vue) | vue | 41 | 1 | 5 | 47 |
| [src/api/aaoSimulation.ts](/src/api/aaoSimulation.ts) | TypeScript | 1,029 | 104 | 154 | 1,287 |
| [src/api/dataClean.ts](/src/api/dataClean.ts) | TypeScript | 60 | 17 | 4 | 81 |
| [src/api/historyData.ts](/src/api/historyData.ts) | TypeScript | 49 | 13 | 4 | 66 |
| [src/api/http.ts](/src/api/http.ts) | TypeScript | 23 | 4 | 6 | 33 |
| [src/api/offline.ts](/src/api/offline.ts) | TypeScript | 58 | 3 | 9 | 70 |
| [src/api/simApi.js](/src/api/simApi.js) | JavaScript | 13 | 3 | 4 | 20 |
| [src/api/simulate.ts](/src/api/simulate.ts) | TypeScript | 13 | 9 | 5 | 27 |
| [src/api/systemParams.ts](/src/api/systemParams.ts) | TypeScript | 77 | 7 | 8 | 92 |
| [src/components/Capsule.js](/src/components/Capsule.js) | JavaScript | 90 | 0 | 48 | 138 |
| [src/components/Octree.js](/src/components/Octree.js) | JavaScript | 256 | 44 | 204 | 504 |
| [src/components/common/AlarmForecastDialog.vue](/src/components/common/AlarmForecastDialog.vue) | vue | 124 | 0 | 16 | 140 |
| [src/components/common/BaselineSimulateDialog.vue](/src/components/common/BaselineSimulateDialog.vue) | vue | 313 | 4 | 47 | 364 |
| [src/components/common/DataCleanDialog.vue](/src/components/common/DataCleanDialog.vue) | vue | 451 | 6 | 61 | 518 |
| [src/components/common/DataCleanEffectDialog.vue](/src/components/common/DataCleanEffectDialog.vue) | vue | 576 | 2 | 63 | 641 |
| [src/components/common/FlowBall.vue](/src/components/common/FlowBall.vue) | vue | 111 | 0 | 12 | 123 |
| [src/components/common/OfflineOptimizeDialog.vue](/src/components/common/OfflineOptimizeDialog.vue) | vue | 3,569 | 28 | 304 | 3,901 |
| [src/components/common/OfflineResultDisplay.vue](/src/components/common/OfflineResultDisplay.vue) | vue | 173 | 0 | 26 | 199 |
| [src/components/common/OfflineSelectDialog.vue](/src/components/common/OfflineSelectDialog.vue) | vue | 226 | 5 | 30 | 261 |
| [src/components/common/OfflineSimulationDialog.vue](/src/components/common/OfflineSimulationDialog.vue) | vue | 2,618 | 34 | 258 | 2,910 |
| [src/components/common/OnlineOptimizationDialog.vue](/src/components/common/OnlineOptimizationDialog.vue) | vue | 1,561 | 21 | 165 | 1,747 |
| [src/components/common/OnlineSelectDialog.vue](/src/components/common/OnlineSelectDialog.vue) | vue | 243 | 5 | 30 | 278 |
| [src/components/common/OnlineSimulationDialog.vue](/src/components/common/OnlineSimulationDialog.vue) | vue | 1,703 | 27 | 174 | 1,904 |
| [src/components/common/SimOverlay.vue](/src/components/common/SimOverlay.vue) | vue | 90 | 3 | 11 | 104 |
| [src/components/common/SimulationParamsSettingsDialog.vue](/src/components/common/SimulationParamsSettingsDialog.vue) | vue | 708 | 14 | 67 | 789 |
| [src/components/common/SystemParamsDialog.vue](/src/components/common/SystemParamsDialog.vue) | vue | 372 | 8 | 41 | 421 |
| [src/components/common/TrendDialog.vue](/src/components/common/TrendDialog.vue) | vue | 319 | 0 | 43 | 362 |
| [src/components/common/TrendInline.vue](/src/components/common/TrendInline.vue) | vue | 215 | 0 | 27 | 242 |
| [src/env.d.ts](/src/env.d.ts) | TypeScript | 9 | 1 | 3 | 13 |
| [src/main.js](/src/main.js) | JavaScript | 14 | 2 | 4 | 20 |
| [src/modules/offline/composables/useOfflineFlow.ts](/src/modules/offline/composables/useOfflineFlow.ts) | TypeScript | 38 | 0 | 6 | 44 |
| [src/modules/offline/configs/aao.optimize.ts](/src/modules/offline/configs/aao.optimize.ts) | TypeScript | 13 | 1 | 1 | 15 |
| [src/modules/offline/configs/aao.simulate.ts](/src/modules/offline/configs/aao.simulate.ts) | TypeScript | 13 | 0 | 1 | 14 |
| [src/modules/offline/configs/mbr.optimize.ts](/src/modules/offline/configs/mbr.optimize.ts) | TypeScript | 13 | 0 | 1 | 14 |
| [src/modules/offline/configs/mbr.simulate.ts](/src/modules/offline/configs/mbr.simulate.ts) | TypeScript | 13 | 0 | 1 | 14 |
| [src/modules/offline/index.ts](/src/modules/offline/index.ts) | TypeScript | 1 | 1 | 1 | 3 |
| [src/modules/offline/pages/OfflineResult.vue](/src/modules/offline/pages/OfflineResult.vue) | vue | 54 | 0 | 6 | 60 |
| [src/modules/offline/pages/OfflineRunner.vue](/src/modules/offline/pages/OfflineRunner.vue) | vue | 212 | 0 | 11 | 223 |
| [src/modules/offline/shared/DatasetPicker.vue](/src/modules/offline/shared/DatasetPicker.vue) | vue | 56 | 0 | 5 | 61 |
| [src/modules/offline/shared/ParamForm.vue](/src/modules/offline/shared/ParamForm.vue) | vue | 91 | 0 | 5 | 96 |
| [src/modules/offline/shared/ResultCharts.vue](/src/modules/offline/shared/ResultCharts.vue) | vue | 84 | 0 | 3 | 87 |
| [src/modules/offline/shared/ResultTable.vue](/src/modules/offline/shared/ResultTable.vue) | vue | 35 | 0 | 3 | 38 |
| [src/modules/offline/shared/RunStatus.vue](/src/modules/offline/shared/RunStatus.vue) | vue | 22 | 0 | 3 | 25 |
| [src/modules/offline/types.ts](/src/modules/offline/types.ts) | TypeScript | 32 | 0 | 5 | 37 |
| [src/modules/router.js](/src/modules/router.js) | JavaScript | 38 | 5 | 3 | 46 |
| [src/stores/useAlarmStore.ts](/src/stores/useAlarmStore.ts) | TypeScript | 64 | 11 | 11 | 86 |
| [src/stores/useOfflineStore.ts](/src/stores/useOfflineStore.ts) | TypeScript | 35 | 1 | 2 | 38 |
| [src/stores/useSimulationParamsStore.ts](/src/stores/useSimulationParamsStore.ts) | TypeScript | 419 | 0 | 37 | 456 |
| [src/style.css](/src/style.css) | CSS | 5 | 0 | 0 | 5 |
| [src/test-offline-result.html](/src/test-offline-result.html) | HTML | 299 | 4 | 21 | 324 |
| [src/utils/fieldMapping.ts](/src/utils/fieldMapping.ts) | TypeScript | 323 | 22 | 24 | 369 |
| [src/view/history/HistoryDataPage.vue](/src/view/history/HistoryDataPage.vue) | vue | 457 | 3 | 34 | 494 |
| [src/view/history/history.less](/src/view/history/history.less) | Less | 116 | 1 | 14 | 131 |
| [src/view/shouye/components/BaselineCard.vue](/src/view/shouye/components/BaselineCard.vue) | vue | 464 | 9 | 38 | 511 |
| [src/view/shouye/components/OfflineCard.vue](/src/view/shouye/components/OfflineCard.vue) | vue | 551 | 11 | 53 | 615 |
| [src/view/shouye/components/OnlineCard.vue](/src/view/shouye/components/OnlineCard.vue) | vue | 476 | 11 | 40 | 527 |
| [src/view/shouye/components/departments/DeptAAO11.vue](/src/view/shouye/components/departments/DeptAAO11.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptAAO12.vue](/src/view/shouye/components/departments/DeptAAO12.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptDeepBedFilter.vue](/src/view/shouye/components/departments/DeptDeepBedFilter.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptDisinfection1.vue](/src/view/shouye/components/departments/DeptDisinfection1.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptDistributeWell.vue](/src/view/shouye/components/departments/DeptDistributeWell.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptEffluentWell.vue](/src/view/shouye/components/departments/DeptEffluentWell.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptGlobalInOut.vue](/src/view/shouye/components/departments/DeptGlobalInOut.vue) | vue | 212 | 6 | 18 | 236 |
| [src/view/shouye/components/departments/DeptHighEffluentSed.vue](/src/view/shouye/components/departments/DeptHighEffluentSed.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptLiftPump.vue](/src/view/shouye/components/departments/DeptLiftPump.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptMBR11.vue](/src/view/shouye/components/departments/DeptMBR11.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptMBR12.vue](/src/view/shouye/components/departments/DeptMBR12.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptSecondaryClarifier1.vue](/src/view/shouye/components/departments/DeptSecondaryClarifier1.vue) | vue | 210 | 4 | 18 | 232 |
| [src/view/shouye/components/departments/DeptSecondaryClarifier2.vue](/src/view/shouye/components/departments/DeptSecondaryClarifier2.vue) | vue | 204 | 4 | 17 | 225 |
| [src/view/shouye/craftAssist.vue](/src/view/shouye/craftAssist.vue) | vue | 346 | 3 | 27 | 376 |
| [src/view/shouye/index.less](/src/view/shouye/index.less) | Less | 1,748 | 58 | 269 | 2,075 |
| [src/view/shouye/index.vue](/src/view/shouye/index.vue) | vue | 496 | 16 | 48 | 560 |
| [src/view/threejs/addFence/index.js](/src/view/threejs/addFence/index.js) | JavaScript | 41 | 24 | 4 | 69 |
| [src/view/threejs/addPeopleModel/index.js](/src/view/threejs/addPeopleModel/index.js) | JavaScript | 24 | 12 | 2 | 38 |
| [src/view/threejs/addPlant/index.js](/src/view/threejs/addPlant/index.js) | JavaScript | 68 | 19 | 5 | 92 |
| [src/view/threejs/addSewageModel/index.js](/src/view/threejs/addSewageModel/index.js) | JavaScript | 51 | 34 | 13 | 98 |
| [src/view/threejs/base/index.js](/src/view/threejs/base/index.js) | JavaScript | 53 | 33 | 14 | 100 |
| [src/view/threejs/index.less](/src/view/threejs/index.less) | Less | 301 | 6 | 59 | 366 |
| [src/view/threejs/index.vue](/src/view/threejs/index.vue) | vue | 709 | 7 | 18 | 734 |
| [src/view/threejs/inspection/index.js](/src/view/threejs/inspection/index.js) | JavaScript | 260 | 49 | 6 | 315 |
| [src/view/threejs/label/index.js](/src/view/threejs/label/index.js) | JavaScript | 24 | 13 | 5 | 42 |
| [src/view/threejs/label/index.vue](/src/view/threejs/label/index.vue) | vue | 47 | 2 | 3 | 52 |
| [src/view/threejs/poolMaterial/index.js](/src/view/threejs/poolMaterial/index.js) | JavaScript | 74 | 10 | 7 | 91 |
| [src/view/threejs/progressBar/index.vue](/src/view/threejs/progressBar/index.vue) | vue | 107 | 1 | 5 | 113 |
| [src/view/threejs/speedControlBar/index.vue](/src/view/threejs/speedControlBar/index.vue) | vue | 107 | 1 | 5 | 113 |
| [src/view/threejs/waterPlane/Water.js](/src/view/threejs/waterPlane/Water.js) | JavaScript | 233 | 69 | 75 | 377 |
| [src/view/threejs/waterPlane/fragmentShader.glsl.js](/src/view/threejs/waterPlane/fragmentShader.glsl.js) | JavaScript | 61 | 8 | 10 | 79 |
| [src/view/threejs/waterPlane/index.js](/src/view/threejs/waterPlane/index.js) | JavaScript | 275 | 80 | 15 | 370 |
| [src/view/threejs/waterPlane/index2.js](/src/view/threejs/waterPlane/index2.js) | JavaScript | 355 | 95 | 29 | 479 |
| [src/view/threejs/waterPlane/vertexShader.glsl.js](/src/view/threejs/waterPlane/vertexShader.glsl.js) | JavaScript | 100 | 7 | 21 | 128 |
| [src/view/trend/TrendPage.vue](/src/view/trend/TrendPage.vue) | vue | 329 | 2 | 41 | 372 |
| [src/view/trend/trend.less](/src/view/trend/trend.less) | Less | 150 | 0 | 18 | 168 |
| [start_backend.bat](/start_backend.bat) | Batch | 30 | 6 | 9 | 45 |
| [start_backend.ps1](/start_backend.ps1) | PowerShell | 32 | 7 | 9 | 48 |
| [tsconfig.json](/tsconfig.json) | JSON with Comments | 19 | 0 | 1 | 20 |
| [vite.config.js](/vite.config.js) | JavaScript | 69 | 9 | 2 | 80 |
| [项目文档.md](/%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3.md) | Markdown | 611 | 0 | 163 | 774 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)