using Prism.Ioc;
using Prism.Modularity;
using Prism.Regions;

namespace NAMESPACE
{
    public class Module : IModule
    {
        public void OnInitialized(IContainerProvider containerProvider)
        {
            var regionManager = containerProvider.Resolve<IRegionManager>();

        }

        public void RegisterTypes(IContainerRegistry containerRegistry) { }
    }
}
