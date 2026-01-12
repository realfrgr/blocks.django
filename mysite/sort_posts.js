document.addEventListener("DOMContentLoaded",function(){

    const form=document.getElementById("sort-form")
    const select=document.getElementById("sort-select")
    const container=document.getElementById("post-container")
    select.addEventListener("change",function(){
        const sortBy = select.value
         if ( !sortBy) return ;
         fetch(`/sort-posts/?sort=${sortBy}`).then(response=>response.json()).then(data=>{
            container.innerHTML="";
            console.log(data)
            data.posts.forEach(post => {
                const postElement = ` <div class="card my-2" style="width: 18rem;">
          <div class="card-body">
            <h5 class="card-title"> ${post.title} </h5>
            <h6 class="card-subtitle mb-2 text-body-secondary">${ post.content }</h6>
            <p>${ post.author }</p>
            <p>${ post.created_at }</p>
            <a href="/post/${ post.id }" class="card-link">More</a>
            <a href="/post/edit/${ post.pk }" class="card-link">Edit</a>
            <a href="/post/${ post.id }/delete" class="card-link">Delete</a>
          </div>
        </div>`;
        container.innerHTML+=postElement;

            });

         }).catch(error=>console.error("Error",error));
         


    });
});