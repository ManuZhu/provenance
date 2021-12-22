window.onload = function (){
    let now = sessionStorage.getItem("step");
    if(now === "21"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '接着进入数据存储界面上传我们收集的数据',
                    element: document.getElementsByClassName("nav-link")[2]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "1");
            window.location.href = "/graph";
        });
        x.start();
    }
}

function guide1_1() {
    let now = sessionStorage.getItem("step");
    if(now === "0"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '如果不知道怎么获得数据，点击这里',
                    element: document.getElementsByClassName("nav-link")[1]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "21");
            window.location.href = "/#five";
        });
        x.start();
    }
    if(now === "21"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '接着进入数据存储界面上传我们收集的数据',
                    element: document.getElementsByClassName("nav-link")[2]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "1");
            window.location.href = "/graph";
        });
        x.start();
    }
}

function guide1_2() {
    let now = sessionStorage.getItem("step");
    if(now === "1") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击上传按钮上传我们的溯源图数据',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[0]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "2");
            window.location.href = "/graph/upload";
        });
        x.start();
    }
    if(now === "3") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击压缩按钮对数据进行压缩',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[26]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "4");
            document.getElementsByClassName("action-icon text-decoration-none")[26].click();
        });
        x.start();
    }
    if(now === "4") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '现在我们需要进一步去除溯源图中的无关信息，将其转化为表示点和边信息的图数据',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[27]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "5");
            document.getElementsByClassName("action-icon text-decoration-none")[27].click();
        });
        x.start();
    }
    if(now === "5") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '现在我们需要将数据转化为我们的神经网络模型能够读入的向量模型',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[28]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "6");
            document.getElementsByClassName("action-icon text-decoration-none")[28].click();
        });
        x.start();
    }
    if(now === "6") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '觉得转化的时间太长？我们可以实时观察进度，同时转化的中间结果也可以在平台主页中看到哦！',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[29]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "8");
            document.getElementsByClassName("action-icon text-decoration-none")[29].click();
        });
        x.start();
    }
    if(now === "7") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '数据不想要了可以随时删除',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[30]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "8");
            document.getElementsByClassName("action-icon text-decoration-none")[30].click();
        });
        x.start();
    }
    if(now === "8") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '现在进入神经网络界面用我们上传的数据来进行入侵行为检测',
                    element: document.getElementsByClassName("nav-link")[3]
                }]
        });
        x.onbeforeexit(() => {
            sessionStorage.setItem("step", "13");
            document.getElementsByClassName("nav-link")[3].click();
        });
        x.start();
    }
}

function guide1_3(){
    let now = sessionStorage.getItem("step");
    if(now === "2") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '这里输入你想要保存的文件名',
                    element: document.getElementsByClassName("form-group required")[0]
                },
                {
                    title: '存储检测一体化',
                    intro: '这里选择你要上传的原始数据文件',
                    element: document.getElementsByClassName("form-group")[1]
                },
                /*{
                    title: '存储检测一体化',
                    intro: '如果你有第一步预处理后的数据也可以在这里上传',
                    element: document.getElementsByClassName("form-group")[2]
                },*/
                {
                    title: '存储检测一体化',
                    intro: '确认无误后点击上传',
                    element: document.getElementsByClassName("btn btn-primary btn-sm")[0]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "3");
            document.getElementsByClassName("btn btn-primary btn-sm")[0].click();
        });
        x.start();
    }
    if(now === "10"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '这里输入你想要保存的神经网络名称',
                    element: document.getElementsByClassName("form-group required")[0]
                },
                {
                    title: '存储检测一体化',
                    intro: '这里选择你要使用模型类型',
                    element: document.getElementsByClassName("form-group required")[1]
                },
                {
                    title: '存储检测一体化',
                    intro: '确认无误后点击上传',
                    element: document.getElementsByClassName("btn btn-primary btn-sm")[0]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "11");
            document.getElementsByClassName("btn btn-primary btn-sm")[0].click();
        });
        x.start();
    }
    if(now === "18"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '训练数据生成',
                    intro: '这里输入你想要保存的神经网络名称',
                    element: document.getElementsByClassName("form-group required")[0]
                },
                {
                    title: '训练数据生成',
                    intro: '为了能够生成数据，我们选择生成对抗网络模型（GAN）',
                    element: document.getElementsByClassName("form-group required")[1]
                },
                {
                    title: '训练数据生成',
                    intro: '确认无误后点击上传',
                    element: document.getElementsByClassName("btn btn-primary btn-sm")[0]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "19");
            document.getElementsByClassName("btn btn-primary btn-sm")[0].click();
        });
        x.start();
    }
}

function guide1_4(){
    let now = sessionStorage.getItem("step");
    if(now === "9") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击这里新建一个神经网络模型',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[0]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "10");
            document.getElementsByClassName("action-icon text-decoration-none")[0].click();
        });
        x.start();
    }
    if(now === "11") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '我们可以点击训练按钮选择样本进行训练',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[5]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "13");
            window.location.href = "/model";
            //document.getElementsByClassName("action-icon text-decoration-none")[5].click();
        });
        x.start();
    }
    if(now === "13") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击开始进行入侵行为检测',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[2]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "14");
            document.getElementsByClassName("action-icon text-decoration-none")[6].click();
        });
        x.start();
    }
    if(now === "17"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '训练数据生成',
                    intro: '点击这里新建一个神经网络模型',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[0]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "18");
            document.getElementsByClassName("action-icon text-decoration-none")[0].click();
        });
        x.start();
    }
    if(now === "19") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '训练数据生成',
                    intro: '生成数据前，我们可以打开日志窗口，在其中我们可以看到系统运行情况和进度',
                    element: document.getElementById("cmd")
                },
                {
                    title: '训练数据生成',
                    intro: '点击按钮开始生成数据',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[5]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "20");
            document.getElementsByClassName("action-icon text-decoration-none")[5].click();
        });
        x.start();
    }
    if(now === "20") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '训练数据生成',
                    intro: '以上就是训练样本生成的全部介绍。'
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "0");
            window.location.href = "/";
        });
        x.start();
    }
    if(now === "22"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '攻击路径展示',
                    intro: '点击开始进行入侵行为检测',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[2]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "23");
            document.getElementsByClassName("action-icon text-decoration-none")[2].click();
        });
        x.start();
    }
}

function guide1_5(){
    let now = sessionStorage.getItem("step");
    if(now === "12") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击选择你的训练数据',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[3]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "13");
            document.getElementsByClassName("action-icon text-decoration-none")[3].click();
        });
        x.start();
    }
}

function guide1_6(){
    let now = sessionStorage.getItem("step");
    if(now === "14") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击选择你的验证样本，它将被当作正常样本',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[3]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "15");
            document.getElementsByClassName("action-icon text-decoration-none")[3].click();
        });
        x.start();
    }
    if(now === "23") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '攻击路径展示',
                    intro: '点击选择你的正常样本',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[1]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "24");
            document.getElementsByClassName("action-icon text-decoration-none")[1].click();
        });
        x.start();
    }
}

function guide1_7(){
    let now = sessionStorage.getItem("step");
    if(now === "15") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '点击选择你要检测的样本',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[4]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "16");
            document.getElementsByClassName("action-icon text-decoration-none")[4].click();
        });
        x.start();
    }
    if(now === "24") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '攻击路径展示',
                    intro: '点击选择你要检测的样本',
                    element: document.getElementsByClassName("action-icon text-decoration-none")[2]
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "25");
            document.getElementsByClassName("action-icon text-decoration-none")[2].click();
        });
        x.start();
    }
}

function guide1_8(){
    let now = sessionStorage.getItem("step");
    if(now === "16") {
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '存储检测一体化',
                    intro: '这里可以下载具有入侵行为的溯源图，从其中可以还原攻击路径并且定位漏洞',
                    element: document.getElementsByClassName("btn btn-primary text-white")[0]
                },
                {
                    title: '存储检测一体化',
                    intro: '这里看到入侵行为检测的结果，其中会显示检测数据中入侵行为和正常行为的数量',
                    element: document.getElementById("tab")
                },
                {
                    title: '存储检测一体化',
                    intro: '以上是有关存储检测一体化的介绍'
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "0");
            window.location.href = "/";
        });
        x.start();
    }
    if(now === "25"){
        let x = introJs();
        x.setOptions({
            steps: [
                {
                    title: '攻击路径展示',
                    intro: '这里可以下载具有入侵行为的溯源图，从其中可以还原攻击路径并且定位漏洞',
                    element: document.getElementsByClassName("btn btn-primary text-white")[0]
                },
                {
                    title: '攻击路径展示',
                    intro: '以上是有关存储检测一体化的所有教程，谢谢！😁'
                }]
        });
        x.onbeforeexit( () => {
            sessionStorage.setItem("step", "0");
            window.location.href = "/";
        });
        x.start();
    }
}

function guide2_1(){
    let x = introJs();
    x.setOptions({
        steps: [
            {
                title: '训练数据生成',
                intro: '首先进入数据检测界面',
                element: document.getElementsByClassName("nav-link")[3]
            }]
    });
    x.onbeforeexit( () => {
        sessionStorage.setItem("step", "17");
        window.location.href = "/model";
    });
    x.start();
}

function guide3_1(){
    let x = introJs();
    x.setOptions({
        steps: [
            {
                title: '攻击路径展示',
                intro: '首先进入数据检测界面',
                element: document.getElementsByClassName("nav-link")[3]
            }]
    });
    x.onbeforeexit( () => {
        sessionStorage.setItem("step", "22");
        window.location.href = "/model";
    });
    x.start();
}