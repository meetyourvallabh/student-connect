self.oninstall = () => {
  caches.open("studentconnect").then(cache => {
    cache
      .addAll(["/", "index.html"])
      .then(() => {
        console.log("cached");
      })
      .catch(err => {
        console.log("err--", err);
      });
  });
};

self.onactivate = () => {
  console.log("activated");
};

self.onfecth = event => {
  event.respondwith(
    caches.match(event.request).then(response => {
      if (response) {
        return response;
      } else {
        return fetch(event.request);
      }
    })
  );
};
