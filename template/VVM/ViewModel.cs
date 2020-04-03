using Prism.Mvvm;

namespace NAMESPACE.ViewModels
{
    public class CLASS : BindableBase
    {
        private string _title = "Prism Application";
        public string Title
        {
            get => this._title;
            set => SetProperty(ref this._title, value);
        }

        public CLASS() { }
    }
}
