// login-script.js

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get form values
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Retrieve user data from localStorage
    const storedUser = JSON.parse(localStorage.getItem('user'));

    // Check if the entered email and password match the stored data
    if (storedUser && storedUser.email === email && storedUser.password === password) {
        alert('Login successful! Welcome ' + storedUser.name);
    } else {
        alert('Invalid email or password. Please try again.');
    }
});
