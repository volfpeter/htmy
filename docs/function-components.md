# Function components

The default and most flexible way to define an `htmy` component is to add a sync or async `htmy(self, context: Context) -> Component` method to a class, often to enhance a pre-existing business object with `htmy` rendering capabilities.

However, in many cases, especially when you're not enhancing an existing class, this ends up being very verbose and requires a lot of boilerplate: you need to define a class, add the necessary properties, and finally implement the `htmy()` method. This is especially impractical when the component has no properties.

Function components address these issues by allowing you to fully skip class creation and define the component simply as a function (well, or method, as we'll see later). This removes the need for any boilerplate, while also making the code more concise and easier to read.

## Function component types

Fundamentally, there are two kinds of function components, both of which may of course be sync or async.

The "classic" function component expects a properties and a context argument, and returns a `Component`: `def fc(props: Props, context: Context) -> Component`. This kind of function component is useful when the component requires properties and also uses the rendering context, for example to get access to the request object, the translation function, a style provider, etc..

Often, components don't need properties, only access to the rendering context. This use-case is addressed by "context-only" function components, which only expect a context argument: `def context_only_fc(context: Context) -> Component`.

You may ask what if a "component" only needs properties, but not the context? Or if it doesn't need either? The answer is these functions are not really components, rather just "component factories". You can find out more about them in the [Components guide](components-guide.md#what-is-a-component-factory).

There is another question that naturally arises: can the instance methods of a class also be function components? The answer is of course yes, which means that in total there are four types of function components.

- Functions with a properties and a context argument.
- Functions with only a context argument.
- Instance methods with a properties and a context argument.
- Instance methods with only a context argument.

## Creating function components

We've discussed the four types of function components and their signatures (protocol/interface definition) in the previous section, but such functions are not automatically components, because they do not have an `htmy()` method.

To turn these functions into components, you need to decorate them with the `@component` decorator. Actually, since all four types of function components look different (remember that methods require the `self` argument as well), the `@component` decorator has one variant for each of them:

- `@component` (and its `@component.function` alias) for functions with a properties and a context argument.
- `@component.context_only` for functions with only a context argument.
- `@component.method` for instance methods with a properties and a context argument.
- `@component.context_only_method` for instance methods with only a context argument.

_Technical note_: the `@component` decorators change the decorated function's signature. After the decorator is applied, the resulting component will be callable with only the function component's properties (if any), and the returned object will have the `htmy(context: Context) -> Component` method that the renderer will call with the context during rendering. As a result, the decorated function will only be executed when the component is rendered.

If it sounded complicated and overly technical, don't worry, function components will feel trivial once you see them in action.

## Examples

Before we dive into the actual components, let's import what we need and create a few utilities, just to have some data to work with. The examples assume that `htmy` is installed.

```python
import asyncio
from dataclasses import dataclass
from typing import Callable

from htmy import ComponentType, Context, Renderer, component, html

@dataclass
class User:
    """User model."""

    username: str
    email: str
    status: str

users = [
    User("alice", "alice@example.ccm", "active"),
    User("bob", "bob@example.ccm", "pending"),
    User("charlie", "charlie@example.ccm", "archived"),
    User("dave", "dave@example.ccm", "active"),
]

def css_provider(key: str) -> str:
    """A dummy style provider function."""
    return key

renderer = Renderer(
    {
        # Add the style provider function to the default rendering context
        # so we can always use it in our components.
        "css": css_provider
    }
)
```

### Functions

First let's create a component that renders a user as a styled list item. The "properties" of this component is the user we want to render, and the context is used to get access to the style provider for styling.

```python
@component
def user_list_item(user: User, context: Context) -> ComponentType:
    """
    Function component that renders a user as a list item.
    """
    css: Callable[[str], str] = context["css"]
    return html.li(
        html.label(user.username),
        class_=css(user.status),
    )
```

Next we create a component renders a list of users. This component is implemented similarly to the list item component, except here we use the `@component.function` decorator (which is just an alias for `@component`), and the decorated function is async, just to showcase that it also works.

```python
@component.function  # @component.function is just an alias for @component
async def user_list(users: list[User], context: Context) -> ComponentType:
    """
    Function component that renders the given list of users.
    """
    css: Callable[[str], str] = context["css"]
    return html.ul(
        *(
            # Render each user using the user_list_item component.
            # Notice that we call the component with only its properties object (the user).
            user_list_item(user)
            for user in users
        ),
        class_=css("unordered-list"),
    )
```

Finally, let's also create a context-only component. This will show a styled page with a heading and the list of users. The pattern is the same as before, but in this case the `@component.context_only` decorator is used and the function only accepts a context argument (no properties).

```python
@component.context_only
def users_page(context: Context) -> ComponentType:
    """
    Context-only function component that renders the users page.
    """
    css: Callable[[str], str] = context["css"]
    return html.div(
        html.h1("Users:", class_=css("heading")),
        # Render users using the user_list component.
        # Notice that we call the component with only its properties (the list of users).
        user_list(users),
        class_=css("page-layout"),
    )
```

With all the components ready, we can now render the `users_page` component and have a look at the result:

```python
rendered = asyncio.run(
    renderer.render(
        # Notice that we call the users_page component with no arguments,
        # since this component has no properties.
        users_page()
    )
)
print(rendered)
```

It wasn't complicated, was it?

### Methods

Having seen how to create and use function components, you probably have a very good idea of how method components work. The only difference is that we use method decorators and that we decorate instance methods.

To reuse some code, we are going to subclass our existing `User` class and add a `profile_page()` and a context-only `table_row()` method component to the subclass. Normally, these methods would be in the `User` class, but using a subclass better suits this guide.

It's important to know that method components can be added even to classes that are themselves components (meaning they have an `htmy()` method). The example below demonstrates this as well.

```python
class EnhancedUser(User):
    """
    `User` subclass with some method components for user rendering.
    """

    @component.method
    def profile_page(self, navbar: html.nav, context: Context) -> ComponentType:
        """
        Method component that renders the user's profile page.
        """
        css: Callable[[str], str] = context["css"]
        return html.div(
            navbar,
            html.div(
                html.p("Username:"),
                html.p(self.username),
                html.p("Email:"),
                html.p(self.email),
                html.p("Status:"),
                html.p(self.status),
                class_=css("profile-card"),
            ),
            class_=css("page-with-navbar"),
        )

    @component.context_only_method
    def table_row(self, context: Context) -> ComponentType:
        """
        Context-only method component that renders the user as a table row.
        """
        css: Callable[[str], str] = context["css"]
        return html.tr(
            html.td(self.username, class_=css("primary")),
            html.td(self.email),
            html.td(self.status),
        )

    def htmy(self, context: Context) -> ComponentType:
        """
        Renders the user as a styled list item.
        """
        css: Callable[[str], str] = context["css"]
        return html.li(
            html.label(self.username),
            class_=css(self.status),
        )
```

As you can see, method components work the same way as function componnts, except the decorated methods have the usual `self` argument, and `@component.method` and `@component.context_only_method` decorators are used instead of `@component` (`@component.function`) and `@component.context_only`.

All that's left to do now is to create an instance of our new, `EnhancedUser` class, render its method components and the instance itself and see the result of our work.

```python
emily = EnhancedUser(username="emily", email="emily@example.ccm", status="active")

rendered = asyncio.run(
    renderer.render(
        html.div(
            # We call the user.profile_page component only with its properties.
            emily.profile_page(html.nav("Navbar")),
            # We call the user.table_row component with no arguments, since
            # this component has no properties.
            emily.table_row(),
            # EnhancedUser instances are also components, because they have an htmy() method.
            emily,
        )
    )
)
print(rendered)
```

That's it!
