exports.handler = async (event) => {
  const name = event.name || 'world';
  return { msg: `Hello ${name} from Node.js!` };
};