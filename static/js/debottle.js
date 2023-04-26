/**
 * @file debottle.js
 * @author YaoSheng
 * @date 2023-04-25 14:47:27
 * @description 节流与防抖
 */

/**
 * 说明：当事件触发时，相应的函数并不会立即触发，而是会等待一定的时间；当事件密集触发时，函数的触发会被频繁的推迟；只有等待了一段时间也没有事件触发，才会真正的执行响应函数；
 *      例如：输入框中频繁的输入内容，频繁触发某个事件，监听浏览器滚动事件等等。
 * 原理：将函数延迟调用，如果在延迟执行时间内再次调用，则清除本次延迟调用，基于新的函数调用重新延迟执行。
 *      如果设置了立即执行，则首次执行时，不会延迟执行而是立即触发函数调用。
 * 缺陷：当设置了立即执行，如果延迟调用刚刚执行完毕就再次调用函数，则两次不会有防抖措施。
 */
/**
 * @descripfang 防抖包装函数
 * @name debounce
 * @param {Function} fn 需要防抖的函数
 * @param {Number} delay 防抖延迟毫秒
 * @param {Boolean} immediate 是否立即执行，默认值 false，首次延迟执行，true 为首次立即执行
 * @param {Function} callback 防抖函数的结果接收回调函数
 */
function debounce(fn, delay, immediate = false, callback = null) {
  let timer = null;

  return function (...args) {
    if (timer) clearTimeout(timer);

    let immediately = immediate && !timer;

    if (immediately) {
      const result = fn.apply(this, args);
      callback && callback.constructor === Function && callback(result);
    }

    timer = setTimeout(() => {
      if (!immediately) {
        const result = fn.apply(this, args);
        callback && callback.constructor === Function && callback(result);
      }
      timer = null;
    }, delay);
  };
}

// 调用示例：
// function add(x, y) {
//     return x + y;
// }
// let foo = debounce(add, 2000, false, (result) => {
//     console.log("result :>> ", result);
// });
// foo(1, 2);
// foo(1, 2);

/**
 * 说明：如果这个事件会被频繁触发，那么节流函数会按照一定的频率来执行函数；不管在这个中间有多少次触发这个事件，执行函数的频率总是固定的；
 *      例如：鼠标移动事件，游戏里的攻击键等等
 * 原理：首次函数调用后会记录调用时间，下次调用时查看距离上一次调用的间隔时间，如果小于设置的间隔时间则不调用函数。
 *      如果大于设置的间隔时间则调用函数。
 */
/**
 * @descripfang 节流包装函数
 * @name throttle
 * @param {Function} fn 需要节流的函数
 * @param {Number} interval 间隔毫秒时间
 * @param {Function} callback 防抖函数的结果接收回调函数
 */
function throttle(fn, interval, callback = null) {
  let last = 0;

  return function (...args) {
    let now = +new Date();

    if (now - last > interval) {
      const result = fn.apply(this, args);
      last = now;
      callback && callback.constructor === Function && callback(result);
    }
  };
}

// 调用示例：
// function add(x, y) {
//     return x + y;
// }
// let foo = throttle(add, 500, (result) => {
//     console.log("result :>> ", result);
// });
// foo(1, 2);
// foo(1, 2);
