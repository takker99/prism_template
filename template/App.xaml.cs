using Prism.Ioc;
using Prism.Modularity;
using Prism.Mvvm;
using Prism.Unity;
using System.Reflection;
using System.Windows;

namespace NAMESPACE
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    // The entry point of the application
    // application の entry point.
    // Do
    //
    // - loading modules
    public partial class App : PrismApplication
    {
        protected override Window CreateShell() => return Container.Resolve<Views.MainWindow>();

        protected override void RegisterTypes(IContainerRegistry containerRegistry) { }

        // Load the modules
        protected override void ConfigureModuleCatalog(IModuleCatalog moduleCatalog)
        {

        }
        // View と ViewModel の命名規則を決める
        //
        // - View:      XXXXX.Views.something
        // - ViewModel: XXXXX.ViewModels.something
        protected override void ConfigureViewModelLocator()
        {
            base.ConfigureViewModelLocator();

            ViewModelLocationProvider.SetDefaultViewTypeToViewModelTypeResolver((viewType) =>
            {
                var viewName = viewType.FullName.Replace(".Views.", ".ViewModels.");
                var viewAssemblyName = viewType.GetTypeInfo().Assembly.FullName;
                var viewModelName = $"{viewName}, {viewAssemblyName}";
                return Type.GetType(viewModelName);
            });
        }
    }
}
