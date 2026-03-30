import apiClient from './api.js';
import { checkAuth, bindLogout } from './auth.js';

checkAuth();
bindLogout();

async function loadRecommendations() {
    try {
        const res = await apiClient.get('/recommendations/today');
        const data = res.data;

        const dietHtml = `
            <div class="d-flex align-items-center mb-3">
                <i class="fas fa-utensils fa-2x text-success me-3"></i>
                <div>
                    <h5>总热量目标</h5>
                    <h3 class="text-success">${data.diet.totalCalories} kcal</h3>
                </div>
            </div>
            <p><i class="fas fa-bread-slice me-2"></i>碳水：${data.diet.carbs}g</p>
            <p><i class="fas fa-egg me-2"></i>蛋白质：${data.diet.protein}g</p>
            <p><i class="fas fa-carrot me-2"></i>蔬菜：${data.diet.veggies}g</p>
            <p class="text-muted mt-3"><i class="fas fa-quote-left me-1"></i>${data.diet.suggestion}</p>
        `;
        document.getElementById('dietRec').innerHTML = dietHtml;

        const exerciseHtml = `
            <div class="d-flex align-items-center mb-3">
                <i class="fas fa-dumbbell fa-2x text-info me-3"></i>
                <div>
                    <h5>推荐运动</h5>
                    <h3 class="text-info">${data.exercise.type}</h3>
                </div>
            </div>
            <p><i class="fas fa-hourglass-half me-2"></i>时长：${data.exercise.duration} 分钟</p>
            <p><i class="fas fa-bolt me-2"></i>预计消耗：${data.exercise.caloriesBurned} 千卡</p>
            <p class="text-muted mt-3"><i class="fas fa-quote-left me-1"></i>${data.exercise.suggestion || '保持运动习惯！'}</p>
        `;
        document.getElementById('exerciseRec').innerHTML = exerciseHtml;
    } catch (error) {
        console.error('加载推荐失败', error);
        document.getElementById('dietRec').innerHTML = '<p class="text-danger text-center">加载失败</p>';
        document.getElementById('exerciseRec').innerHTML = '<p class="text-danger text-center">加载失败</p>';
    }
}

loadRecommendations();