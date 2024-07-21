// script.js

document.getElementById('sign-up-form').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get form values
    const role = document.querySelector('input[name="role"]:checked').value;
    const name = document.getElementById('name').value;
    const country = document.getElementById('country').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Save to localStorage
    const user = {
        role: role,
        name: name,
        country: country,
        email: email,
        password: password
    };

    localStorage.setItem('user', JSON.stringify(user));

    alert('Sign up successful! You can now log in.');
    window.location.href = 'C:\\Users\\Lenovo\\Desktop\\GP\\web\\Login.html'; // Redirect to login page
});
