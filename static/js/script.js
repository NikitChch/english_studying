function fixImages() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (!img.complete) {
            img.classList.add('loading');
        }
        
        if (img.complete && img.naturalHeight === 0 && !img.classList.contains('error')) {
            img.classList.add('error');
            handleImageError(img);
        }
        
        img.addEventListener('load', function() {
            this.classList.remove('loading');
            this.classList.remove('error');
        });
        
        img.addEventListener('error', function() {
            this.classList.remove('loading');
            this.classList.add('error');
            handleImageError(this);
        });
    });
}

function replaceExternalImage(imgElement) {
    const imageType = getImageType(imgElement);
    const localSrc = getLocalImagePath(imageType);
    if (localSrc) {
        imgElement.src = localSrc;
        imgElement.classList.remove('error');
        imgElement.classList.add('loading');
    }
}

function getImageType(imgElement) {
    const src = imgElement.src.toLowerCase();
    const alt = imgElement.alt.toLowerCase();
    const parentClass = imgElement.parentElement?.className || '';
    if (src.includes('grammar') || alt.includes('грамматик') || parentClass.includes('grammar')) {
        return 'grammar';
    } else if (src.includes('vocabulary') || alt.includes('словар') || parentClass.includes('vocabulary')) {
        return 'vocabulary';
    } else if (src.includes('team') || alt.includes('команд') || parentClass.includes('team')) {
        return 'team';
    } else if (src.includes('contact') || alt.includes('контакт') || parentClass.includes('contact')) {
        return 'contact';
    } else {
        return 'general';
    }
}

function getLocalImagePath(type) {
    const localImages = {
        'grammar': '/static/images/grammar-placeholder.jpg',
        'vocabulary': '/static/images/vocabulary-placeholder.jpg',
        'team': '/static/images/team-placeholder.jpg',
        'contact': '/static/images/contact-placeholder.jpg',
        'general': '/static/images/general-placeholder.jpg'
    };
    return localImages[type] || localImages['general'];
}

function createDefaultProfileSVG() {
    const svgString = `<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r="75" fill="#667eea"/>
        <circle cx="75" cy="60" r="25" fill="white"/>
        <circle cx="75" cy="120" r="40" fill="white"/>
        <text x="75" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#667eea" font-weight="bold">USER</text>
    </svg>`;
    return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
}

function checkOnlineStatus() {
    if (!navigator.onLine) {
        document.body.classList.add('offline');
        showNotification('Вы работаете в оффлайн-режиме. Некоторые функции могут быть ограничены.', 'warning');
        replaceAllExternalImages();
    } else {
        document.body.classList.remove('offline');
    }
}

function replaceAllExternalImages() {
    const images = document.querySelectorAll('img[src*="http"]');
    images.forEach(img => {
        if (!img.complete || img.naturalHeight === 0) {
            replaceExternalImage(img);
        }
    });
}

function showNotification(message, type = 'info') {
    const oldNotifications = document.querySelectorAll('.notification-toast');
    oldNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed notification-toast`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 1050; min-width: 300px; max-width: 400px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function loadReviews() {
    const reviews = JSON.parse(localStorage.getItem('reviews')) || [];
    const list = document.getElementById('reviewsList');
    if (!list) return;
    list.innerHTML = reviews.length 
        ? reviews.map(r => `
            <div class="mb-4 p-3 border rounded">
                <strong>${r.author}</strong> — ${r.date}<br>
                ${r.type === 'teacher' ? `О преподавателе: <em>${r.teacher}</em><br>` : ''}
                <em>${r.text}</em>
            </div>
        `).join('')
        : '<p>Отзывов пока нет.</p>';
}

function initReviewForm() {
    const reviewForm = document.getElementById('reviewForm');
    const reviewType = document.getElementById('reviewType');
    const teacherSelect = document.getElementById('teacherSelect');
    
    if (!reviewForm || !reviewType) return;
    
    reviewType.addEventListener('change', e => {
        if (teacherSelect) {
            teacherSelect.style.display = e.target.value === 'teacher' ? 'block' : 'none';
        }
    });
    
    reviewForm.addEventListener('submit', e => {
        e.preventDefault();
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        if (!isLoggedIn) {
            showNotification('Чтобы оставить отзыв, необходимо войти в систему.', 'warning');
            return;
        }
        
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        const type = document.getElementById('reviewType').value;
        const author = userData.name || 'Аноним';
        const text = document.getElementById('reviewText').value;
        const teacher = type === 'teacher' ? document.getElementById('teacherName').value : null;
        
        const review = {
            id: Date.now(),
            type,
            teacher,
            author,
            text,
            date: new Date().toLocaleString('ru-RU')
        };
        
        const reviews = JSON.parse(localStorage.getItem('reviews')) || [];
        reviews.unshift(review);
        localStorage.setItem('reviews', JSON.stringify(reviews));
        showNotification('Спасибо за ваш отзыв!', 'success');
        document.getElementById('reviewForm').reset();
        loadReviews();
    });
}

function updateUserMenu() {
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const profileLink = document.getElementById('profileLink');
    const diaryLink = document.getElementById('diaryLink');
    const userStatus = document.getElementById('userStatus');
    const userName = document.getElementById('userName');
    const logoutBtn = document.getElementById('logoutBtn');
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');

    if (isLoggedIn && userData.name) {
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (profileLink) profileLink.style.display = 'block';
        if (diaryLink) diaryLink.style.display = 'block';
        if (userStatus) userStatus.style.display = 'inline-flex';
        if (userName) userName.textContent = userData.name;
        if (logoutBtn) logoutBtn.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (registerLink) registerLink.style.display = 'block';
        if (profileLink) profileLink.style.display = 'none';
        if (diaryLink) diaryLink.style.display = 'none';
        if (userStatus) userStatus.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userData');
    localStorage.removeItem('userType');
    localStorage.removeItem('userDiary');
    updateUserMenu();
    window.location.href = '/';
}

function updateMenuVisibility() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const diaryLink = document.getElementById('diaryLink');
    const profileLink = document.getElementById('profileLink');
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');

    if (diaryLink) {
        diaryLink.style.display = isLoggedIn ? 'block' : 'none';
    }
    if (profileLink) {
        profileLink.style.display = isLoggedIn ? 'block' : 'none';
    }
    if (loginLink) {
        loginLink.style.display = isLoggedIn ? 'none' : 'block';
    }
    if (registerLink) {
        registerLink.style.display = isLoggedIn ? 'none' : 'block';
    }
}

function getAllStudents() {
    const users = JSON.parse(localStorage.getItem('users')) || [];
    return users.filter(user => user.type === 'student');
}

function getAllTeachers() {
    const users = JSON.parse(localStorage.getItem('users')) || [];
    return users.filter(user => user.type === 'teacher');
}

function getStudentGrades(studentId) {
    return JSON.parse(localStorage.getItem(`grades_${studentId}`)) || [];
}

function saveStudentGrades(studentId, grades) {
    localStorage.setItem(`grades_${studentId}`, JSON.stringify(grades));
}

function addGrade(studentId, gradeData) {
    const grades = getStudentGrades(studentId);
    gradeData.id = Date.now();
    gradeData.date = new Date().toLocaleDateString('ru-RU');
    grades.push(gradeData);
    saveStudentGrades(studentId, grades);
    return gradeData;
}

function getStudentAttendance(studentId) {
    return JSON.parse(localStorage.getItem(`attendance_${studentId}`)) || [];
}

function saveStudentAttendance(studentId, attendance) {
    localStorage.setItem(`attendance_${studentId}`, JSON.stringify(attendance));
}

function markAttendance(studentId, date, status, subject) {
    const attendance = getStudentAttendance(studentId);
    const existingRecord = attendance.find(record => record.date === date && record.subject === subject);
    
    if (existingRecord) {
        existingRecord.status = status;
    } else {
        attendance.push({
            id: Date.now(),
            date,
            subject,
            status
        });
    }
    
    saveStudentAttendance(studentId, attendance);
}

function getSubjects() {
    return ['Грамматика', 'Словарь', 'Аудирование', 'Разговорная практика', 'Письмо', 'Чтение'];
}

function initializeDefaultData() {
    if (!localStorage.getItem('groups')) {
        const groups = ['Группа A1', 'Группа A2', 'Группа B1', 'Группа B2', 'Группа C1'];
        localStorage.setItem('groups', JSON.stringify(groups));
    }
    
    if (!localStorage.getItem('subjects')) {
        const subjects = getSubjects();
        localStorage.setItem('subjects', JSON.stringify(subjects));
    }
}

function initScrollToTop() {
    const scrollToTopButton = document.getElementById('scrollToTop');
    if (scrollToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopButton.classList.add('visible');
            } else {
                scrollToTopButton.classList.remove('visible');
            }
        });
        scrollToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

function containsBadWords(text, badWordsList) {
    if (!text || !badWordsList) return false;
    
    const lowerText = text.toLowerCase();
    return badWordsList.some(word => {
        const lowerWord = word.toLowerCase();
        return lowerText.includes(lowerWord);
    });
}

function filterBadWords(text, badWordsList) {
    if (!text || !badWordsList) return text;
    
    let filteredText = text;
    badWordsList.forEach(word => {
        const regex = new RegExp(word, 'gi');
        filteredText = filteredText.replace(regex, '*'.repeat(word.length));
    });
    
    return filteredText;
}

function loadReviewsWithFilter(filterTopic = '') {
    const reviews = JSON.parse(localStorage.getItem('reviews')) || [];
    const badWords = JSON.parse(localStorage.getItem('badWords')) || [
        'плохой', 'ужасный', 'отвратительный', 'кошмар', 'гадость'
    ];
    
    const list = document.getElementById('reviewsList');
    if (!list) return;
    
    let filteredReviews = reviews;
    
    if (filterTopic) {
        filteredReviews = reviews.filter(review => review.topic === filterTopic);
    }
    
    filteredReviews = filteredReviews.map(review => ({
        ...review,
        text: filterBadWords(review.text, badWords)
    }));
    
    if (filteredReviews.length === 0) {
        list.innerHTML = '<p class="text-muted">Отзывов по выбранной теме пока нет.</p>';
        return;
    }
    
    list.innerHTML = filteredReviews.map(review => `
        <div class="review-item mb-4 p-3 border rounded">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <strong class="text-primary">${review.author}</strong>
                    <span class="badge bg-secondary ms-2">${review.topic}</span>
                </div>
                <small class="text-muted">${review.date}</small>
            </div>
            ${review.type === 'teacher' ? `<p class="mb-2"><small class="text-success">О преподавателе: <strong>${review.teacher}</strong></small></p>` : ''}
            <p class="mb-0" style="line-height: 1.5;">${review.text}</p>
        </div>
    `).join('');
}

function getScheduleData() {
    const scheduleDataElement = document.getElementById('schedule-data');
    if (scheduleDataElement) {
        return JSON.parse(scheduleDataElement.textContent);
    }
    return {};
}

function getTeacherScheduleData() {
    const teacherScheduleElement = document.getElementById('teacher-schedule');
    if (teacherScheduleElement) {
        return JSON.parse(teacherScheduleElement.textContent);
    }
    return [];
}

function filterScheduleByWeek(schedule, period) {
    const daysOrder = {
        'Понедельник': 1,
        'Вторник': 2,
        'Среда': 3,
        'Четверг': 4,
        'Пятница': 5,
        'Суббота': 6,
        'Воскресенье': 7
    };

    const sortedSchedule = [...schedule].sort((a, b) => {
        return daysOrder[a.day] - daysOrder[b.day];
    });

    if (period === 'current') {
        return sortedSchedule;
    } else if (period === 'next') {
        return sortedSchedule.map(lesson => ({
            ...lesson,
            day: lesson.day + ' (След. неделя)'
        }));
    }
    
    return sortedSchedule;
}

function showStudentSchedule(period) {
    const user = JSON.parse(localStorage.getItem('userData'));
    if (!user || !user.group) {
        document.getElementById('scheduleContent').innerHTML = '<p class="text-muted">Группа не указана в профиле.</p>';
        return;
    }

    const scheduleData = getScheduleData();
    const userGroup = user.group;
    
    let userSchedule = [];
    if (scheduleData[userGroup]) {
        userSchedule = scheduleData[userGroup];
    } else {
        document.getElementById('scheduleContent').innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Расписание для вашей группы (${userGroup}) пока не составлено.
            </div>
        `;
        return;
    }
    
    const scheduleContent = document.getElementById('scheduleContent');
    
    if (userSchedule.length === 0) {
        scheduleContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Расписание для вашей группы (${userGroup}) пока не составлено.
            </div>
        `;
        return;
    }

    const filteredSchedule = filterScheduleByWeek(userSchedule, period);
    
    if (filteredSchedule.length === 0) {
        scheduleContent.innerHTML = '<p class="text-muted">На выбранный период занятий нет.</p>';
        return;
    }

    scheduleContent.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped schedule-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-calendar-day me-2"></i>День</th>
                        <th><i class="fas fa-clock me-2"></i>Время</th>
                        <th><i class="fas fa-book me-2"></i>Предмет</th>
                        <th><i class="fas fa-chalkboard-teacher me-2"></i>Преподаватель</th>
                        <th><i class="fas fa-door-open me-2"></i>Аудитория</th>
                    </tr>
                </thead>
                <tbody>
                    ${filteredSchedule.map(lesson => `
                        <tr>
                            <td><strong>${lesson.day}</strong></td>
                            <td>${lesson.time}</td>
                            <td>
                                <span class="badge bg-primary schedule-badge">${lesson.subject}</span>
                            </td>
                            <td>${lesson.teacher}</td>
                            <td>${lesson.classroom || '<span class="text-success">Онлайн</span>'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="mt-3 text-muted">
            <small><i class="fas fa-info-circle me-1"></i>Показано ${filteredSchedule.length} занятий</small>
        </div>
    `;
    
    document.querySelectorAll('#scheduleContent').closest('.content-card').querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

function loadTeacherSchedule() {
    const teacherSchedule = getTeacherScheduleData();
    const scheduleContent = document.getElementById('teacherScheduleContent');
    
    if (!teacherSchedule || teacherSchedule.length === 0) {
        scheduleContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Расписание не найдено.
            </div>
        `;
        return;
    }

    scheduleContent.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped schedule-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-calendar-day me-2"></i>День</th>
                        <th><i class="fas fa-clock me-2"></i>Время</th>
                        <th><i class="fas fa-book me-2"></i>Предмет</th>
                        <th><i class="fas fa-users me-2"></i>Группа</th>
                        <th><i class="fas fa-door-open me-2"></i>Аудитория</th>
                    </tr>
                </thead>
                <tbody>
                    ${teacherSchedule.map(lesson => `
                        <tr>
                            <td><strong>${lesson.day}</strong></td>
                            <td>${lesson.time}</td>
                            <td>
                                <span class="badge bg-primary schedule-badge">${lesson.subject}</span>
                            </td>
                            <td>
                                <span class="badge bg-success schedule-badge">${lesson.group}</span>
                            </td>
                            <td>${lesson.classroom || '<span class="text-success">Онлайн</span>'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="mt-3 text-muted">
            <small><i class="fas fa-info-circle me-1"></i>Показано ${teacherSchedule.length} занятий</small>
        </div>
    `;
}

function filterTeacherSchedule(group) {
    const teacherSchedule = getTeacherScheduleData();
    const filteredLessons = group ? teacherSchedule.filter(lesson => lesson.group === group) : teacherSchedule;
    const scheduleContent = document.getElementById('teacherScheduleContent');
    
    if (filteredLessons.length === 0) {
        scheduleContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Занятий для выбранной группы не найдено.
            </div>
        `;
        return;
    }

    scheduleContent.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped schedule-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-calendar-day me-2"></i>День</th>
                        <th><i class="fas fa-clock me-2"></i>Время</th>
                        <th><i class="fas fa-book me-2"></i>Предмет</th>
                        <th><i class="fas fa-users me-2"></i>Группа</th>
                        <th><i class="fas fa-door-open me-2"></i>Аудитория</th>
                    </tr>
                </thead>
                <tbody>
                    ${filteredLessons.map(lesson => `
                        <tr>
                            <td><strong>${lesson.day}</strong></td>
                            <td>${lesson.time}</td>
                            <td>
                                <span class="badge bg-primary schedule-badge">${lesson.subject}</span>
                            </td>
                            <td>
                                <span class="badge bg-success schedule-badge">${lesson.group}</span>
                            </td>
                            <td>${lesson.classroom || '<span class="text-success">Онлайн</span>'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="mt-3 text-muted">
            <small><i class="fas fa-info-circle me-1"></i>Показано ${filteredLessons.length} занятий для ${group ? 'группы ' + group : 'всех групп'}</small>
        </div>
    `;
}

function selectProduct(productId, productName) {
    document.getElementById('productId').value = productId;
    
    const selectedProductElement = document.querySelector('.selected-product');
    const selectedProductNameElement = document.getElementById('selectedProductName');
    
    selectedProductNameElement.textContent = productName;
    selectedProductElement.style.display = 'block';
    
    document.getElementById('submitOrderBtn').disabled = false;
    
    document.querySelectorAll('.product-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    const selectedCard = document.querySelector(`[data-product-id="${productId}"]`).closest('.product-card');
    selectedCard.classList.add('selected');
    
    document.getElementById('orderForm').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

function initProductSelection() {
    document.querySelectorAll('.select-product-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productName = this.getAttribute('data-product-name');
            selectProduct(productId, productName);
        });
    });
}

function initOrderForm() {
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', function(e) {
            const productId = document.getElementById('productId').value;
            if (!productId) {
                e.preventDefault();
                showNotification('Пожалуйста, выберите продукт перед оформлением заказа', 'warning');
                return;
            }
            
            const submitBtn = document.getElementById('submitOrderBtn');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Оформление...';
                submitBtn.disabled = true;
            }
        });
    }
}

let sidebarInitialized = false;

function initSidebarToggle() {
    if (sidebarInitialized) return;
    sidebarInitialized = true;

    const toggleBtn = document.getElementById('toggleSidebar');
    const toggleIcon = document.getElementById('toggleIcon');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (!toggleBtn || !sidebar) return;

    function updateSidebarState() {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            sidebar.classList.remove('collapsed');
            if (sidebar.classList.contains('mobile-open')) {
                toggleIcon?.classList.remove('fa-chevron-right');
                toggleIcon?.classList.add('fa-chevron-left');
            } else {
                toggleIcon?.classList.remove('fa-chevron-left');
                toggleIcon?.classList.add('fa-chevron-right');
            }

            toggleBtn.onclick = () => {
                sidebar.classList.toggle('mobile-open');
                if (sidebar.classList.contains('mobile-open')) {
                    toggleIcon?.classList.remove('fa-chevron-right');
                    toggleIcon?.classList.add('fa-chevron-left');
                } else {
                    toggleIcon?.classList.remove('fa-chevron-left');
                    toggleIcon?.classList.add('fa-chevron-right');
                }
            };

        } else {
            sidebar.classList.remove('mobile-open');
            const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
                mainContent.style.marginLeft = '70px';
                mainContent.style.width = 'calc(100% - 70px)';
                toggleIcon?.classList.remove('fa-chevron-left');
                toggleIcon?.classList.add('fa-chevron-right');
            } else {
                sidebar.classList.remove('collapsed');
                mainContent.style.marginLeft = '250px';
                mainContent.style.width = 'calc(100% - 250px)';
                toggleIcon?.classList.remove('fa-chevron-right');
                toggleIcon?.classList.add('fa-chevron-left');
            }

            toggleBtn.onclick = () => {
                const willCollapse = !sidebar.classList.contains('collapsed');
                sidebar.classList.toggle('collapsed', willCollapse);
                if (willCollapse) {
                    mainContent.style.marginLeft = '70px';
                    mainContent.style.width = 'calc(100% - 70px)';
                    toggleIcon?.classList.remove('fa-chevron-left');
                    toggleIcon?.classList.add('fa-chevron-right');
                    localStorage.setItem('sidebarCollapsed', 'true');
                } else {
                    mainContent.style.marginLeft = '250px';
                    mainContent.style.width = 'calc(100% - 250px)';
                    toggleIcon?.classList.remove('fa-chevron-right');
                    toggleIcon?.classList.add('fa-chevron-left');
                    localStorage.setItem('sidebarCollapsed', 'false');
                }
            };
        }
    }

    updateSidebarState();
    window.addEventListener('resize', updateSidebarState);
}

function preventHorizontalScroll() {
    document.documentElement.style.overflowX = 'hidden';
    document.body.style.overflowX = 'hidden';
    const checkOverflow = () => {
        const elements = document.querySelectorAll('*');
        elements.forEach(el => {
            if (el.scrollWidth > el.clientWidth && !el.classList.contains('sidebar')) {
                el.style.overflowX = 'hidden';
            }
        });
    };
    window.addEventListener('load', checkOverflow);
    window.addEventListener('resize', checkOverflow);
}

document.addEventListener('DOMContentLoaded', function() {
    checkOnlineStatus();
    window.addEventListener('online', checkOnlineStatus);
    window.addEventListener('offline', checkOnlineStatus);

    initializeDefaultData();

    initSidebarToggle();

    const header = document.querySelector('.modern-header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;
            e.preventDefault();
            const targetId = href.substring(1);
            if (!targetId) return;
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                const headerHeight = document.querySelector('.modern-header')?.offsetHeight || 0;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    const animatedElements = document.querySelectorAll('.feature-card, .content-card, .stat-card, .responsive-img');
    animatedElements.forEach(el => {
        observer.observe(el);
    });

    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }

    initScrollToTop();
    fixImages();
    preventHorizontalScroll();
    loadReviews();
    initReviewForm();

    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    function enhanceNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link, .sidebar-nav .nav-link');
        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            if (linkPath && (currentPath === linkPath || (currentPath.includes(linkPath) && linkPath !== '/'))) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    enhanceNavigation();

    const cards = document.querySelectorAll('.feature-card, .content-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.01)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const shapes = document.querySelectorAll('.hero-shape');
        shapes.forEach((shape, index) => {
            const speed = 0.5 + (index * 0.1);
            shape.style.transform = `translateY(${scrolled * speed}px) rotate(${scrolled * 0.1}deg)`;
        });
    });

    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showNotification('Сообщение отправлено! Мы свяжемся с вами в ближайшее время.', 'success');
            contactForm.reset();
        });
    }

    setTimeout(fixImages, 2000);
    updateUserMenu();
    updateMenuVisibility();
    initProductSelection();
    initOrderForm();
    document.querySelectorAll('.select-product-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productName = this.getAttribute('data-product-name');
            selectProduct(productId, productName);
        });
    });

    function adjustTopOffset() {
        const topBar = document.getElementById('topBar');
        const mainArea = document.querySelector('.main-content-area');
        if (topBar && mainArea) {
            const height = topBar.offsetHeight;
            mainArea.style.marginTop = (height + 5) + 'px';
        }
    }
    window.addEventListener('load', adjustTopOffset);
    window.addEventListener('resize', adjustTopOffset);
    setTimeout(adjustTopOffset, 500);
});

document.getElementById('logoutBtn')?.addEventListener('click', logout);