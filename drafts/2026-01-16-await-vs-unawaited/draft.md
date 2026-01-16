The Difference Between 'await' and 'unawaited' Cost Me 2 Days

## The Scenario

It was 2am on a Sunday, and I was hunched over my laptop, trying to figure out why my Flutter app's checkout flow was broken. Users were reporting that the "Place Order" button was doing nothing, and I couldn't reproduce the issue locally.

I had spent the last six hours scouring the codebase, stepping through the debugger, and checking every edge case I could think of. But nothing seemed to be wrong. The API call was firing, the UI was updating, and there were no errors in the logs. Yet somehow, the order wasn't being placed.

As I stared at the code, I started to doubt my understanding of async/await in Dart. Surely, I had this down - I'd been writing Flutter apps for over 5 years. But clearly, there was something I was missing.

## The Setup

If you've worked with Dart and Flutter for a while, you're probably familiar with the `await` keyword. It's a crucial part of working with asynchronous code, allowing you to pause execution and wait for a Future to complete before moving on.

What you may not know, however, is that there's another keyword - `unawaited` - that can also be used with Futures. And the difference between the two can have some serious consequences in production.

In this article, I'm going to take you on the journey I went through to understand the nuances of `await` and `unawaited`, and how it ultimately helped me fix that pesky checkout bug. Along the way, we'll dive deep into the internals of Dart's asynchronous programming model, explore the trade-offs involved, and learn some best practices to avoid the pitfalls I encountered.

## What's Actually Happening Under the Hood

To understand the difference between `await` and `unawaited`, we need to take a look at how Dart handles asynchronous code.

When you call a method that returns a `Future`, Dart creates a new execution context and schedules the asynchronous operation to run in the background. This means that the current method can continue executing without waiting for the asynchronous operation to complete.

The `await` keyword is used to pause the current execution context and wait for the Future to complete before moving on. This is often the most intuitive way to work with asynchronous code, as it allows you to write sequential, synchronous-looking code.

However, there are times when you might not want to wait for a Future to complete. Perhaps you're making a fire-and-forget API call, or you're kicking off a background task that doesn't need to block the current flow. In these cases, you can use the `unawaited` function from the `dart:async` library.

```dart
// ❌ The bug/mistake (what I wrote first)
void handleSubmit() {
  unawaited(api.submit(data));
  setState(() => isLoading = false); // Runs immediately!
}
```

The `unawaited` function takes a Future and "swallows" any errors that might occur during its execution. This means that if the Future completes with an error, that error will be ignored, and your app will continue running as if nothing happened.

This might seem like a convenient way to fire off an asynchronous operation and move on, but as I learned the hard way, it can also lead to some unexpected behavior.

**The Problem:**

In my checkout flow, I was using `unawaited` to kick off the API call to place the order, and then immediately setting the `isLoading` state to `false` to hide the loading spinner. The logic looked something like this:

```dart
// ❌ The bug/mistake (what I wrote first)
void handleSubmit() {
  unawaited(api.submit(data));
  setState(() => isLoading = false); // Runs immediately!
}
```

The issue here is that the `setState` call runs immediately, before the API call has a chance to complete. This means that the loading spinner will disappear even if the order hasn't been placed yet.

Now, you might be thinking, "But wait, shouldn't the API call be happening in the background? Why would the loading spinner disappear prematurely?"

The answer lies in the way Dart handles asynchronous operations.

When you call a method that returns a Future, Dart creates a new execution context and schedules the asynchronous operation to run in the background. However, the current method continues executing immediately, without waiting for the asynchronous operation to complete.

In the case of `unawaited`, Dart doesn't pause the current execution context at all. It simply schedules the asynchronous operation and moves on, allowing the `setState` call to run immediately.

This is where the problem lies. By the time the API call completes, the loading spinner has already been hidden, and the user is left wondering what's happening.

**The Lesson:**

The key difference between `await` and `unawaited` is that `await` pauses the current execution context and waits for the Future to complete before moving on, while `unawaited` simply schedules the asynchronous operation and continues executing the current method.

In my case, I should have used `await` to ensure that the API call completed before hiding the loading spinner:

```dart
// ✅ The fix (what I learned)
Future<void> handleSubmit() async {
  setState(() => isLoading = true);
  await api.submit(data); // Actually wait
  if (!mounted) return;
  setState(() => isLoading = false);
}
```

By using `await`, I'm telling Dart to pause the current execution context and wait for the API call to complete before moving on to the `setState` call. This ensures that the loading spinner is only hidden once the order has been placed, providing a smooth and reliable user experience.

## Why It Works This Way

The design decision to have `unawaited` "swallow" any errors that might occur during the asynchronous operation was a deliberate choice by the Dart team. The rationale behind this is that if you're using `unawaited`, you're likely not interested in the result of the asynchronous operation, and you don't want any errors to disrupt the flow of your app.

However, this choice can also lead to subtle bugs, as I discovered in my checkout flow. If an error occurs in the asynchronous operation, it will be silently ignored, and your app will continue running as if nothing happened. This can make it much harder to debug issues, as you may not even be aware that something has gone wrong.

To mitigate this, the Dart team recommends that you use `await` whenever possible, and only use `unawaited` in cases where you truly don't care about the outcome of the asynchronous operation. This ensures that any errors that occur will be properly handled and surfaced, making it easier to debug and maintain your code.

## The Common Pitfalls

The difference between `await` and `unawaited` is a common source of confusion for Dart developers, and it's easy to make mistakes, especially when working with complex, production-ready apps.

One common pitfall I've seen is using `unawaited` to fire off multiple asynchronous operations in a loop, without realizing that the operations are not being properly awaited. This can lead to race conditions, where the UI updates before all the operations have completed.

```dart
// ❌ The bug/mistake (what I wrote first)
void handleBatchSubmit(List<Data> data) {
  for (final item in data) {
    unawaited(api.submit(item));
  }
  setState(() => isLoading = false);
}
```

In this example, the `isLoading` state is set to `false` immediately, even though the API calls may still be in progress. This can result in a confusing user experience, where the loading spinner disappears before the batch of orders has been placed.

Another common pitfall is forgetting to handle the case where the widget is no longer mounted when the asynchronous operation completes. This can happen if the user navigates away from the screen while the operation is in progress.

```dart
// ❌ The bug/mistake (what I wrote first)
Future<void> handleSubmit() async {
  setState(() => isLoading = true);
  await api.submit(data);
  setState(() => isLoading = false);
}
```

In this example, if the user navigates away from the screen while the API call is in progress, the `setState` call to hide the loading spinner will still run, even though the widget is no longer mounted. This can lead to errors and unexpected behavior.

To avoid these pitfalls, it's important to always check the widget's mount status before updating the UI, and to properly await all asynchronous operations, even if you're using `unawaited` in some cases.

## How to Do It Right

Based on the lessons I've learned, here are some best practices for working with `await` and `unawaited` in Dart:

1. **Use `await` by default**: Unless you have a specific reason to use `unawaited`, always use `await` to ensure that asynchronous operations complete before moving on.

2. **Handle errors properly**: When using `await`, make sure to handle any errors that might occur during the asynchronous operation. This could involve wrapping the `await` in a `try/catch` block, or using the `catchError` method on the Future.

3. **Check mount status**: Whenever you're updating the UI after an asynchronous operation, make sure to check the widget's mount status to ensure that the widget is still on the screen. You can do this by calling `if (!mounted) return;` before updating the state.

4. **Avoid `unawaited` in loops**: If you need to fire off multiple asynchronous operations in a loop, consider using `Future.wait` or `Future.forEach` to ensure that all the operations complete before moving on.

5. **Document your use of `unawaited`**: If you do choose to use `unawaited`, make sure to document why you're doing it and what the expected behavior is. This will help other developers (including your future self) understand the reasoning behind your choice.

6. **Use `unawaited` sparingly**: `unawaited` should be used only in cases where you truly don't care about the outcome of the asynchronous operation. In most cases, it's better to use `await` and handle errors properly.

By following these best practices, you can avoid the kinds of subtle bugs and production issues that I encountered in my checkout flow, and write more reliable and maintainable Dart code.

## Practical Application

Now that we've explored the nuances of `await` and `unawaited`, let's look at a few real-world examples of how these concepts apply in actual Flutter apps.

**Example 1: Submitting a Form**

In a typical form submission flow, you'll want to use `await` to ensure that the API call completes before updating the UI:

```dart
// ✅ The right way
Future<void> handleSubmit() async {
  setState(() => isLoading = true);
  try {
    await api.submitForm(formData);
    if (!mounted) return;
    setState(() => isLoading = false);
    Navigator.pushNamed(context, '/success');
  } catch (e) {
    if (!mounted) return;
    setState(() => isLoading = false);
    showErrorDialog(context, e);
  }
}
```

By using `await`, we're ensuring that the API call completes before hiding the loading spinner and navigating to the success screen. We're also handling any errors that might occur during the API call, and showing an error dialog to the user if something goes wrong.

**Example 2: Sending Analytics Events**

In contrast, if you're sending analytics events to track user behavior, you might not care about the outcome of the asynchronous operation. In this case, `unawaited` might be a reasonable choice:

```dart
// ✅ The right way
void trackEvent(AnalyticsEvent event) {
  unawaited(analytics.logEvent(event));
}
```

By using `unawaited`, we're fire-and-forgetting the analytics event, and not waiting for the operation to complete. This ensures that the user's experience is not disrupted if there's an issue with the analytics call.

Of course, you'll still want to handle any errors that might occur during the analytics call in a more centralized way, such as by logging them to a crash reporting service. But for the purposes of the specific user flow, using `unawaited` can be a reasonable choice.

**Example 3: Batching API Calls**

Earlier, we saw an example of using `unawaited` in a loop to batch API calls, which can lead to race conditions and unexpected behavior. Here's a better way to handle this scenario:

```dart
// ✅ The right way
Future<void> handleBatchSubmit(List<Data> data) async {
  setState(() => isLoading = true);
  await Future.wait(data.map((item) => api.submit(item)));
  if (!mounted) return;
  setState(() => isLoading = false);
}
```

By using `Future.wait`, we're ensuring that all the API calls complete before updating the UI. This way, the loading spinner will only disappear once all the orders have been placed, providing a smooth and reliable user experience.

## Trade-offs & Alternatives

While `await` and `unawaited` are powerful tools for working with asynchronous code in Dart, they're not the only options available. Depending on your specific use case, there may be simpler or more complex alternatives to consider.

**Simpler Alternatives**

For very simple asynchronous operations, you might not even need to use `await` or `unawaited`. Instead, you can use the `.then()` method to chain together multiple asynchronous operations:

```dart
api.submitForm(formData)
  .then((_) => Navigator.pushNamed(context, '/success'))
  .catchError((e) => showErrorDialog(context, e));
```

This approach can be more concise and readable for simple cases, but it can also become unwieldy as the complexity of your asynchronous logic increases.

**More Complex Alternatives**

If you're working with more complex asynchronous flows, you might consider using a library like `rx_dart` (the Dart implementation of RxJS) to manage your asynchronous operations. This can provide a more powerful and expressive way to handle things like error handling, retries, and backpressure.

```dart
api.submitForm(formData)
  .doOnData((_) => Navigator.pushNamed(context, '/success'))
  .doOnError((e) => showErrorDialog(context, e))
  .listen((_) {}, onError: (_) {});
```

However, the tradeoff is that you'll need to invest more time in learning the Rx paradigm and its associated concepts, which may not be necessary for all use cases.

Ultimately, the choice between `await`, `unawaited`, and other asynchronous patterns will depend on the specific requirements of your app and the complexity of the asynchronous logic you're dealing with. The key is to choose the approach that best balances readability, maintainability, and performance for your particular use case.

## Key Takeaway

The difference between `await` and `unawaited` in Dart is a subtle but important one, and it's a lesson I had to learn the hard way through a painful 2-day debugging session.

The key insight I gained is that `await` and `unawaited` are not just syntactic sugar - they represent fundamentally different ways of handling asynchronous operations. `await` pauses the current execution context and waits for the Future to complete, while `unawaited` simply schedules the asynchronous operation and moves on.

This distinction can have serious consequences in production, as I discovered when my checkout flow broke due to the premature disappearance of the loading spinner. By understanding the underlying mechanics and learning to use `await` and `unawaited` judiciously, I was able to write more reliable and maintainable Dart code that could withstand the rigors of a real-world app.

The lesson here is that when it comes to asynchronous programming, the devil is in the details. It's not enough to just know the syntax - you need to deeply understand the implications of the choices you make, and be willing to dig into the internals of the language and framework you're working with. Only then can you truly master the art of writing robust, production-ready code.