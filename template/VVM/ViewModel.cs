using Prism.Mvvm;
using Reactive.Bindings;
using Reactive.Bindings.Extensions;

namespace MODULE_NAMESPACE.ViewModels
{
    public class VIEW : BindableBase, System.IDisposable
    {
        public VIEW() { }

        void System.IDisposable.Dispose() => this._disposables.Dispose();
        private System.Reactive.Disposables.CompositeDisposable _disposables = new System.Reactive.Disposables.CompositeDisposable();
    }
}
