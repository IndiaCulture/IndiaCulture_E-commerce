


document.addEventListener("DOMContentLoaded", function () {
    const videos = document.querySelectorAll(".insta-video-card video");

    videos.forEach((video) => {
      // Desktop: Play on hover, pause on leave
      video.addEventListener("mouseenter", () => {
        video.muted = true;
        video.play();
      });

      video.addEventListener("mouseleave", () => {
        video.pause();
        video.currentTime = 0; // Optional: reset to start
      });

      // Mobile: Play on first touch
      video.addEventListener("touchstart", () => {
        if (video.paused) {
          video.muted = true;
          video.play();
        } else {
          video.pause();
          video.currentTime = 0;
        }
      });
    });
  });

document.addEventListener("DOMContentLoaded", function () {
    const videos = document.querySelectorAll(".review-video-card video");

    videos.forEach((video) => {
      // Desktop: Play on hover, pause on leave
      video.addEventListener("mouseenter", () => {
        video.muted = true;
        video.play();
      });

      video.addEventListener("mouseleave", () => {
        video.pause();
        video.currentTime = 0; // Optional: reset to start
      });

      // Mobile: Play on first touch
      video.addEventListener("touchstart", () => {
        if (video.paused) {
          video.muted = true;
          video.play();
        } else {
          video.pause();
          video.currentTime = 0;
        }
      });
    });
  });

  // NAV

   // Elements
            const navbarCollapse = document.getElementById('mainNavbar');
            const closeBtn = document.getElementById('mobileCloseBtn');
            const backdrop = document.getElementById('sideDrawerBackdrop');
            const navbarToggler = document.querySelector('.navbar-toggler');

            // Show/hide backdrop on menu open/close
            function updateBackdrop() {
                if (navbarCollapse.classList.contains('show')) {
                    backdrop.classList.add('active');
                    document.body.classList.add('offcanvas-backdrop');
                } else {
                    backdrop.classList.remove('active');
                    document.body.classList.remove('offcanvas-backdrop');
                }
            }

            // Listen for Bootstrap collapse events
            navbarCollapse.addEventListener('shown.bs.collapse', updateBackdrop);
            navbarCollapse.addEventListener('hidden.bs.collapse', updateBackdrop);

            // Close menu on close button click
            closeBtn.addEventListener('click', function() {
                const collapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
                collapse.hide();
            });

            // Close menu on backdrop click
            backdrop.addEventListener('click', function() {
                const collapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
                collapse.hide();
            });

            // Optional: Hide backdrop if window resized to desktop
            window.addEventListener('resize', function() {
                if (window.innerWidth >= 992) {
                    backdrop.classList.remove('active');
                    document.body.classList.remove('offcanvas-backdrop');
                }
            });


// SIGNIN
const signInForm = document.getElementById('signInForm');
        const signUpForm = document.getElementById('signUpForm');
        const toggleBtn = document.getElementById('toggleBtn');
        const panelText = document.getElementById('panelText');

        toggleBtn.addEventListener('click', () => {
            const isSignUp = signUpForm.classList.contains('active');
            if (isSignUp) {
                signUpForm.classList.remove('active');
                signInForm.classList.add('active');
                toggleBtn.textContent = 'Sign Up';
                panelText.innerHTML = "Don't have an account?<br>Sign up and join us!";
            } else {
                signInForm.classList.remove('active');
                signUpForm.classList.add('active');
                toggleBtn.textContent = 'Sign In';
                panelText.innerHTML = "Already have an account?<br>Just sign in.";
            }
        });

        // Animate form transitions
        function animateFormSwitch(form) {
            form.style.opacity = 0;
            setTimeout(() => {
                form.style.opacity = 1;
            }, 200);
        }
        toggleBtn.addEventListener('click', () => {
            animateFormSwitch(signInForm);
            animateFormSwitch(signUpForm);
        });

// Handle home animation
const animatedElements = document.querySelectorAll('.animate-on-scroll');

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('start-animation');
      observer.unobserve(entry.target); // stop observing after animation starts
    }
  });
});

animatedElements.forEach(el => {
  observer.observe(el);
});

// Handle auto submit on mycart quantity change
