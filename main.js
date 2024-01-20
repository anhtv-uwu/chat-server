function create_user_list(username){
    // <div class="user">
    //     <img src="https://vnn-imgs-a1.vgcloud.vn/image1.ictnews.vn/_Files/2020/02/25/trend-avatar-6.jpg"
    //     alt="photo">
    //   <div class="details">
    //     <div>id</div>
    //   </div>
    // </div>
    let box = document.getElementById('box');
    let user = document.createElement('div');
    user.classList.add('user');
    let img = document.createElement('img');
    img.src = "https://vnn-imgs-a1.vgcloud.vn/image1.ictnews.vn/_Files/2020/02/25/trend-avatar-6.jpg";
    img.alt = "photo";
    let details = document.createElement('div');
    details.classList.add('details');
    let id = document.createElement('div');
    id.innerHTML = username;
    details.appendChild(id);
    user.appendChild(img);
    user.appendChild(details);
    box.appendChild(user);
}