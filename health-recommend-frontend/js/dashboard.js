import apiClient from './api.js';
import { checkAuth, getUser, bindLogout } from './auth.js';

checkAuth();
bindLogout();

const user = getUser();
if (user) {
    document.getElementById('username').textContent = user.username || '用户';
}

const today = new Date();
document.getElementById('todayDate').textContent = today.toLocaleDateString('zh-CN', { year:'numeric', month:'long', day:'numeric' });

async function loadDashboard() {
    try {
        const res = await apiClient.get('/dashboard/overview');
        const data = res.data;

        if (data.intake.length > 0) {
            document.getElementById('todayIntake').textContent = data.intake[data.intake.length-1];
        }
        if (data.expenditure.length > 0) {
            document.getElementById('todayExpenditure').textContent = data.expenditure[data.expenditure.length-1];
        }
        const lastWeight = data.weights.filter(w => w !== null).pop();
        document.getElementById('latestWeight').textContent = lastWeight ? lastWeight.toFixed(1) : '--';

        const weightChart = echarts.init(document.getElementById('weightChart'));
        weightChart.setOption({
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'category', data: data.weightDates },
            yAxis: { type: 'value', name: 'kg' },
            series: [{ data: data.weights, type: 'line', smooth: true, lineStyle: { color: '#4361ee' } }]
        });

        const calorieChart = echarts.init(document.getElementById('calorieChart'));
        calorieChart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['摄入', '消耗'] },
            xAxis: { data: data.dates },
            yAxis: { name: '千卡' },
            series: [
                { name: '摄入', type: 'bar', data: data.intake, color: '#f72585' },
                { name: '消耗', type: 'bar', data: data.expenditure, color: '#4cc9f0' }
            ]
        });
    } catch (error) {
        console.error('加载仪表盘数据失败', error);
    }
}

loadDashboard();