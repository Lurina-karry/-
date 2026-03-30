// data-entry.js
import apiClient from './api.js';
import { checkAuth, bindLogout } from './auth.js';

checkAuth();
bindLogout();

// ---------- 身体指标 ----------
document.getElementById('bodyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    let data = Object.fromEntries(formData);
    const requestData = {
        weight: parseFloat(data.weight),
        height: parseFloat(data.height),
        age: parseInt(data.age),
        gender: data.gender,
        record_date: data.record_date
    };
    try {
        await apiClient.post('/body-metrics', requestData);
        alert('身体指标保存成功');
        e.target.reset();
        const today = new Date().toISOString().split('T')[0];
        document.querySelector('#bodyForm [name="record_date"]').value = today;
        fetchUserWeight(); // 更新体重用于运动估算
    } catch (error) {
        alert('保存失败：' + (error.response?.data?.detail || error.message));
    }
});

// ---------- 饮食自动估算（增强错误处理） ----------
const estimateFoodBtn = document.getElementById('estimateFoodBtn');
const foodNameInput = document.getElementById('foodNameInput');
const caloriesInput = document.getElementById('caloriesInput');

if (estimateFoodBtn) {
    estimateFoodBtn.addEventListener('click', async () => {
        const food = foodNameInput.value.trim();
        if (!food) {
            alert('请输入食物名称');
            return;
        }
        estimateFoodBtn.disabled = true;
        estimateFoodBtn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> 估算中...';
        try {
            const res = await apiClient.post('/estimate/food', { food_name: food });
            caloriesInput.value = res.data.calories;
            alert(`估算成功！${res.data.name} 每100克约 ${res.data.calories} 千卡`);
        } catch (error) {
            let errorMsg = '估算失败：' + (error.response?.data?.detail || '请手动输入热量');
            const status = error.response?.status;
            if (status === 404) {
                errorMsg = `未找到「${food}」的热量信息，请手动输入。`;
            } else if (status === 502 || status === 504) {
                errorMsg = '外部服务暂时不可用，请稍后重试。';
            } else if (status === 422) {
                errorMsg = error.response?.data?.detail || '输入错误，请检查食物名称。';
            }
            alert(errorMsg);
        } finally {
            estimateFoodBtn.disabled = false;
            estimateFoodBtn.innerHTML = '<i class="fas fa-magic"></i> 自动估算热量';
        }
    });
}

// 饮食记录提交
document.getElementById('dietForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    data.calories = parseFloat(data.calories);
    try {
        await apiClient.post('/diet-records', data);
        alert('饮食记录保存成功');
        e.target.reset();
        const today = new Date().toISOString().split('T')[0];
        document.querySelector('#dietForm [name="record_date"]').value = today;
    } catch (error) {
        alert('保存失败：' + (error.response?.data?.detail || error.message));
    }
});

// ---------- 运动自动估算 ----------
let currentWeight = 70;
async function fetchUserWeight() {
    try {
        const res = await apiClient.get('/dashboard/overview');
        const weights = res.data.weights.filter(w => w !== null);
        if (weights.length > 0) {
            currentWeight = weights[weights.length - 1];
        }
    } catch (error) {
        console.warn('无法获取最新体重，使用默认值70kg');
    }
}
fetchUserWeight();

const estimateExerciseBtn = document.getElementById('estimateExerciseBtn');
const exerciseTypeInput = document.getElementById('exerciseTypeInput');
const durationInput = document.getElementById('durationInput');
const caloriesBurnedInput = document.getElementById('caloriesBurnedInput');

if (estimateExerciseBtn) {
    estimateExerciseBtn.addEventListener('click', async () => {
        const exercise = exerciseTypeInput.value.trim();
        const duration = parseFloat(durationInput.value);
        if (!exercise) {
            alert('请输入运动类型');
            return;
        }
        if (isNaN(duration) || duration <= 0) {
            alert('请输入有效时长');
            return;
        }
        estimateExerciseBtn.disabled = true;
        estimateExerciseBtn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> 估算中...';
        try {
            const res = await apiClient.post('/estimate/exercise', {
                exercise_type: exercise,
                duration: duration,
                weight: currentWeight
            });
            caloriesBurnedInput.value = Math.round(res.data.total_calories);
        } catch (error) {
            alert('估算失败：' + (error.response?.data?.detail || '请手动输入消耗热量'));
        } finally {
            estimateExerciseBtn.disabled = false;
            estimateExerciseBtn.innerHTML = '<i class="fas fa-magic"></i> 自动估算消耗';
        }
    });
}

// 运动记录提交
document.getElementById('exerciseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    data.duration = parseInt(data.duration);
    if (data.calories_burned) data.calories_burned = parseFloat(data.calories_burned);
    try {
        await apiClient.post('/exercise-records', data);
        alert('运动记录保存成功');
        e.target.reset();
        const today = new Date().toISOString().split('T')[0];
        document.querySelector('#exerciseForm [name="record_date"]').value = today;
    } catch (error) {
        alert('保存失败：' + (error.response?.data?.detail || error.message));
    }
});