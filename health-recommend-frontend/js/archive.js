import apiClient from './api.js';
import { checkAuth, bindLogout } from './auth.js';

console.log('🚀 archive.js 最终版 2026-03-23-final');

checkAuth();
bindLogout();

let currentType = 'body';
const recordListEl = document.getElementById('recordList');
const tabs = document.querySelectorAll('#recordTypeTab .nav-link');

tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
        e.preventDefault();
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentType = tab.dataset.type;
        loadRecords(currentType);
    });
});

function safeFormatDate(value) {
    if (value == null) return '日期未知';
    try {
        if (typeof value === 'string') {
            if (value.includes('T')) {
                return value.split('T')[0];
            }
            return value;
        }
        if (value instanceof Date) {
            return value.toISOString().split('T')[0];
        }
        return String(value);
    } catch (e) {
        console.warn('日期格式化失败', value, e);
        return '日期错误';
    }
}

async function loadRecords(type) {
    recordListEl.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-pulse fa-2x"></i><p class="mt-2">加载中...</p></div>';
    try {
        const res = await apiClient.get(`/records/${type}`);
        const records = res.data;
        console.log(`[${type}] 原始数据示例:`, records?.[0]);

        if (!records || records.length === 0) {
            recordListEl.innerHTML = '<div class="alert alert-info text-center">暂无记录</div>';
            return;
        }

        const html = records.map(record => {
            const dateField = record.record_date || record.recordDate || record.date;
            const date = safeFormatDate(dateField);

            if (type === 'body') {
                const weight = record.weight ?? '--';
                const bodyFat = record.body_fat ?? record.bodyFat ?? '--';
                return `<div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-weight-scale text-primary me-2"></i>
                            <strong>${date}</strong>
                        </div>
                        <span>体重: ${weight}kg | 体脂: ${bodyFat}%</span>
                    </div>
                </div>`;
            } 
            else if (type === 'diet') {
                const food = record.food_name ?? record.foodName ?? '未知';
                const meal = record.meal_type ?? record.mealType ?? '其他';
                const calories = record.calories ?? 0;
                return `<div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-utensils text-success me-2"></i>
                            <strong>${date}</strong>
                        </div>
                        <span>${food} (${meal}) : ${calories} kcal</span>
                    </div>
                </div>`;
            } 
            else if (type === 'exercise') {
                const exercise = record.exercise_type ?? record.exerciseType ?? '未知';
                const duration = record.duration ?? 0;
                const burned = record.calories_burned ?? record.caloriesBurned ?? 0;
                return `<div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-running text-warning me-2"></i>
                            <strong>${date}</strong>
                        </div>
                        <span>${exercise} ${duration}分钟, 消耗 ${burned} kcal</span>
                    </div>
                </div>`;
            }
            return '';
        }).join('');
        recordListEl.innerHTML = html;
    } catch (error) {
        console.error('加载记录失败', error);
        recordListEl.innerHTML = '<div class="alert alert-danger text-center">加载失败，请稍后重试</div>';
    }
}

loadRecords(currentType);