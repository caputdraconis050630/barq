
const { handler } = require('./index.js');
const event = {"name": "Barq"};
(async () => {
    const result = await handler(event);
    console.log(result);
})();
